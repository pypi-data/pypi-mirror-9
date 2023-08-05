#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "ip2cc.h"

#define ip_t ip2cc_ip_t

enum ip2cc_node_type {
  nt_undefined = 0,
  nt_subtree = 1,
  nt_value = 2
};

struct ip2cc_node {
  enum ip2cc_node_type type;
  union {
    char *value;
    struct ip2cc_node *subtree;
  } ref;
};

typedef struct ip2cc_node node_t;


void ip2cc_parse_ip(const char *raw_ip, ip_t ip) {
  size_t index = 0;
  while (*raw_ip) {
    if (*raw_ip == '.') {
      index++;
    } else {
      ip[index] = ip[index] * 10 + *raw_ip - '0';
    }
    raw_ip++;
  }
}

static void free_node(node_t *node) {
  switch (node->type) {
    case nt_subtree:
      ip2cc_free(node->ref.subtree);
      break;
    case nt_value:
      free(node->ref.value);
      break;
    default:
      break;
  }
}

void ip2cc_free(node_t *tree)
{
  for (int i = 0; i < 256; i++) {
    free_node(tree + i);
  }
  free(tree);
}

node_t *ip2cc_make_tree()
{
  node_t *tree = calloc(256, sizeof(node_t));
  return tree;
}

static int _store(node_t *tree, ip_t ip, unsigned char step, const char *value)
{
  node_t *node = tree + ip[3 - step];
  if (! step) {
    switch (node->type) {
      case nt_value:
        free(node->ref.value);
        break;
      default:
        break;
    }
    node->type = nt_value;
    size_t len = strlen(value);
    node->ref.value = malloc(len + 1);
    strcpy(node->ref.value, value);
    return 0;
  } else {
    if (node->type == nt_undefined) {
      node->type = nt_subtree;
      node->ref.subtree = ip2cc_make_tree();
    }
    return _store(node->ref.subtree, ip, step - 1, value);
  }
}

int ip2cc_store(node_t *tree, const char *raw_ip, const char *value)
{
  ip_t ip = {0};
  ip2cc_parse_ip(raw_ip, ip);
  return _store(tree, ip, 3, value);
}

static char *_lookup(node_t *tree, ip_t ip, int step)
{
  node_t *node = tree + ip[3 - step];
  if (node->type == nt_value) {
    return node->ref.value;
  }
  if (step && node->type == nt_subtree) {
    return _lookup(node->ref.subtree, ip, step - 1);
  }
  return NULL;
}

char *ip2cc_lookup(node_t *tree, const char *raw_ip)
{
  ip_t ip = {0};
  ip2cc_parse_ip(raw_ip, ip);
  return _lookup(tree, ip, 3);
}

static size_t tree_size(node_t *tree, size_t value_len, unsigned char level)
{
  node_t *node;
  size_t len = 0;
  switch (level) {
    case 0:
      len = 256 * value_len;
      break;
    default:
      len = 256 * (2 + value_len);
      for (int i = 0; i < 256; i++) {
        node = tree + i;
        if (node->type == nt_subtree) {
          len += tree_size(node->ref.subtree, value_len, level - 1);
        }
      }
      break;
  }
  return len;
}

static void dump_tree(node_t *tree, size_t value_len, size_t offset, char level, unsigned char *data)
{
  node_t *node;
  unsigned char item_size;
  if (level) {
    item_size = 2 + value_len;
  } else {
    item_size = value_len;
  }
  size_t header_size = 256 * item_size;
  unsigned char *write_to;
  size_t end = offset + header_size;
  size_t subtree_size;
  for (int i = 0; i < 256; i++) {
    node = tree + i;
    write_to = data + offset + i * item_size;
    if (level) {
      switch (node->type) {
        case nt_value:
          *(write_to) = 0xff;
          *(write_to + 1) = 0xff;
          memcpy(write_to + 2, node->ref.value, value_len);
          break;
        case nt_undefined:
          *(write_to) = 0xff;
          *(write_to + 1) = 0xff;
          break;
        case nt_subtree:
          subtree_size = tree_size(node->ref.subtree, value_len, level - 1);
          dump_tree(node->ref.subtree, value_len, end, level - 1, data);
          *(write_to) = (end & 0xff000000) >> 24;
          *(write_to + 1) = (end & 0xff0000) >> 16;
          *(write_to + 2) = (end & 0xff00) >> 8;
          *(write_to + 3) = end & 0xff;
          end += subtree_size;
          break;
      }
    } else if (node->type == nt_value) {
      memcpy(write_to, node->ref.value, value_len);
    }
  }
}

size_t ip2cc_write_tree(node_t *tree, size_t value_len, FILE *fp)
{
  size_t data_size = tree_size(tree, value_len, 3);
  unsigned char *data = calloc(data_size, 1);
  dump_tree(tree, value_len, 0, 3, data);
  fwrite(data, 1, data_size, fp);
  free(data);
  return data_size;
}

static int _read_tree(node_t *tree, size_t value_len, FILE *fp, size_t offset, unsigned char level, unsigned char *buf)
{
  node_t *node;
  size_t subtree_addr;
  unsigned char item_size;
  int res;
  if (level) {
    item_size = value_len + 2;
  } else {
    item_size = value_len;
  }
  for (int i = 0; i < 256; i++) {
    fseek(fp, offset + i * item_size, SEEK_SET);
    fread(buf, 1, item_size, fp);
    node = tree + i;
    if (level) {
      if (buf[0] == 0xff && buf[1] == 0xff) {
        if (buf[2] != 0) {
          node->type = nt_value;
          node->ref.value = calloc(value_len + 1, 1);
          memcpy(node->ref.value, buf + 2, value_len);
        }
      } else {
        node->type = nt_subtree;
        node->ref.subtree = ip2cc_make_tree();
        subtree_addr = (buf[0] << 24) + (buf[1] << 16) + (buf[2] << 8) + buf[3];
        res = _read_tree(node->ref.subtree, value_len, fp, subtree_addr, level - 1, buf);
        if (res) {
          return res;
        }
      }
    } else {
      if (node->type != nt_undefined) {
        return 1;
      }
      if (buf[0]) {
        node->type = nt_value;
        node->ref.value = calloc(value_len + 1, 1);
        memcpy(node->ref.value, buf, value_len);
      }
    }
  }
  return 0;
}

int ip2cc_read_tree(node_t *tree, size_t value_len, FILE *fp)
{
  unsigned char *buf = malloc(value_len + 2);
  int res = _read_tree(tree, value_len, fp, 0, 3, buf);
  free(buf);
  return res;
}
