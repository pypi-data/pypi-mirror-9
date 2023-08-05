
typedef struct ip2cc_node *ip2cc_tree_t;

typedef unsigned char ip2cc_ip_t[4];

void ip2cc_free(ip2cc_tree_t);

void ip2cc_parse_ip(const char *, ip2cc_ip_t);

ip2cc_tree_t ip2cc_make_tree();

int ip2cc_store(ip2cc_tree_t, const char *, const char *);

char *ip2cc_lookup(ip2cc_tree_t, const char *);

size_t ip2cc_write_tree(ip2cc_tree_t, size_t, FILE *);

int ip2cc_read_tree(ip2cc_tree_t, size_t, FILE *);
