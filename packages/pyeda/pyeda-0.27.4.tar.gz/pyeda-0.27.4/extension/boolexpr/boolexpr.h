/*
** Filename: boolexpr.h
*/


#ifndef BOOLEXPR_H
#define BOOLEXPR_H


#ifdef __cplusplus
extern "C" {
#endif


#define CHECK_NULL(y, x) \
do { \
    if ((y = x) == NULL) \
        return NULL; \
} while (0)


#define CHECK_NULL_1(y, x, temp) \
do { \
    if ((y = x) == NULL) { \
        BoolExpr_DecRef(temp); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_2(y, x, t0, t1) \
do { \
    if ((y = x) == NULL) { \
        BoolExpr_DecRef(t0); \
        BoolExpr_DecRef(t1); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_3(y, x, t0, t1, t2) \
do { \
    if ((y = x) == NULL) { \
        BoolExpr_DecRef(t0); \
        BoolExpr_DecRef(t1); \
        BoolExpr_DecRef(t2); \
        return NULL; \
    } \
} while (0)


#define CHECK_NULL_N(y, x, n, temps) \
do { \
    if ((y = x) == NULL) { \
        for (size_t i = 0; i < n; ++i) \
            BoolExpr_DecRef(temps[i]); \
        return NULL; \
    } \
} while (0)


/* Type checks */
#define IS_ZERO(ex)  (((ex)->type) == ZERO)
#define IS_ONE(ex)   (((ex)->type) == ONE)
#define IS_COMP(ex)  (((ex)->type) == COMP)
#define IS_VAR(ex)   (((ex)->type) == VAR)
#define IS_OR(ex)    (((ex)->type) == OP_OR)
#define IS_AND(ex)   (((ex)->type) == OP_AND)
#define IS_XOR(ex)   (((ex)->type) == OP_XOR)
#define IS_EQ(ex)    (((ex)->type) == OP_EQ)
#define IS_NOT(ex)   (((ex)->type) == OP_NOT)
#define IS_IMPL(ex)  (((ex)->type) == OP_IMPL)
#define IS_ITE(ex)   (((ex)->type) == OP_ITE)


/* Category checks */
#define IS_ATOM(ex)   (((ex)->type) >> 3 == 0x0) // 0***
#define IS_CONST(ex)  (((ex)->type) >> 2 == 0x0) // 00**
#define IS_LIT(ex)    (((ex)->type) >> 1 == 0x2) // 010*
#define IS_OP(ex)     (((ex)->type) >> 3 == 0x1) // 1***


/* Flag definitions */
#define SIMPLE 0x01
#define NNF    0x02


/* Flag checks */
#define IS_SIMPLE(ex) (((ex)->flags) & SIMPLE)
#define IS_NNF(ex)    (((ex)->flags) & NNF)


/* Other */
#define COMPLEMENTARY(x, y) \
    (IS_LIT(x) && IS_LIT(y) && \
     ((x)->data.lit.uniqid == -((y)->data.lit.uniqid)))

#define DUAL(t) (OP_OR + OP_AND - t)


/* Expression types */
typedef enum {
    ZERO = 0x00,
    ONE  = 0x01,

    LOGICAL   = 0x02,
    ILLOGICAL = 0x03,

    COMP = 0x04,
    VAR  = 0x05,

    OP_OR  = 0x08,
    OP_AND = 0x09,
    OP_XOR = 0x0A,
    OP_EQ  = 0x0B,

    OP_NOT  = 0x0C,
    OP_IMPL = 0x0D,
    OP_ITE  = 0x0E,
} BoolExprType;


/* Expression flags */
typedef unsigned char BoolExprFlags;


struct BoolExpr {
    int refcount;

    BoolExprType type;
    BoolExprFlags flags;

    union {
        /* constant */
        unsigned int pcval;

        /* literal */
        struct {
            struct BoolExprVector *lits;
            long uniqid;
        } lit;

        /* operator */
        struct BoolExprArray *xs;
    } data;
};


struct BoolExprIter {
    bool done;
    struct BoolExpr *ex;
    size_t index;
    struct BoolExprIter *it;
};


struct BoolExprArray {
    size_t length;
    struct BoolExpr **items;
};


struct BoolExprArray2 {
    size_t length;
    struct BoolExprArray **items;
};


struct BoolExprVector {
    size_t length;
    size_t capacity;
    struct BoolExpr **items;
};


struct BoolExprDict {
    size_t (*prehash)(struct BoolExpr *);
    size_t length;
    size_t pridx;
    struct BoolExprDictItem **items;
};


struct BoolExprSet {
    size_t (*prehash)(struct BoolExpr *);
    size_t length;
    size_t pridx;
    struct BoolExprSetItem **items;
};


/* Constant expressions */
extern struct BoolExpr Zero;
extern struct BoolExpr One;
extern struct BoolExpr Logical;
extern struct BoolExpr Illogical;

extern struct BoolExpr * IDENTITY[16];
extern struct BoolExpr * DOMINATOR[16];


/*
** Return a literal expression.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * Literal(struct BoolExprVector *lits, long uniqid);


/*
** Return an operator expression.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * Or(size_t n, struct BoolExpr **xs);
struct BoolExpr * Nor(size_t n, struct BoolExpr **xs);
struct BoolExpr * And(size_t n, struct BoolExpr **xs);
struct BoolExpr * Nand(size_t n, struct BoolExpr **xs);
struct BoolExpr * Xor(size_t n, struct BoolExpr **xs);
struct BoolExpr * Xnor(size_t n, struct BoolExpr **xs);
struct BoolExpr * Equal(size_t n, struct BoolExpr **xs);
struct BoolExpr * Unequal(size_t n, struct BoolExpr **xs);

struct BoolExpr * OrN(size_t n, ...);
struct BoolExpr * NorN(size_t n, ...);
struct BoolExpr * AndN(size_t n, ...);
struct BoolExpr * NandN(size_t n, ...);
struct BoolExpr * XorN(size_t n, ...);
struct BoolExpr * XnorN(size_t n, ...);
struct BoolExpr * EqualN(size_t n, ...);
struct BoolExpr * UnequalN(size_t n, ...);

struct BoolExpr * Not(struct BoolExpr *x);
struct BoolExpr * Implies(struct BoolExpr *p, struct BoolExpr *q);
struct BoolExpr * ITE(struct BoolExpr *s, struct BoolExpr *d1, struct BoolExpr *d0);


/*
** Increment the reference count of an expression.
*/
struct BoolExpr * BoolExpr_IncRef(struct BoolExpr *);


/*
** Decrement the reference count of an expression.
*/
void BoolExpr_DecRef(struct BoolExpr *);


/*
** Return the depth of an expression tree.
**
** 1. An atom node (constant or literal) has zero depth.
** 2. A branch node (operator) has depth equal to the maximum depth of
**    its children (arguments) plus one.
*/
unsigned long BoolExpr_Depth(struct BoolExpr *);


/*
** Return the size of an expression tree.
**
** 1. An atom node (constant or literal) has size one.
** 2. A branch node (operator) has size equal to the sum of its children's
**    sizes plus one.
*/
unsigned long BoolExpr_Size(struct BoolExpr *);


/* Return the number of atoms in an expression tree. */
unsigned long BoolExpr_AtomCount(struct BoolExpr *);


/* Return the number of operators in an expression tree. */
unsigned long BoolExpr_OpCount(struct BoolExpr *);


/* Return true if the expression is in disjunctive normal form. */
bool BoolExpr_IsDNF(struct BoolExpr *);

/* Return true if the expression is in conjunctive normal form. */
bool BoolExpr_IsCNF(struct BoolExpr *);


/*
** Return an expression with NOT operators pushed down through dual operators.
**
** Specifically, perform the following transformations:
**     ~(a | b | c ...) <=> ~a & ~b & ~c ...
**     ~(a & b & c ...) <=> ~a | ~b | ~c ...
**     ~(s ? d1 : d0) <=> s ? ~d1 : ~d0
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_PushDownNot(struct BoolExpr *);


/*
** Return a simplified expression.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_Simplify(struct BoolExpr *);


/*
** Convert all N-ary operators to binary operators.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_ToBinary(struct BoolExpr *);


/*
** Return an expression in negation normal form.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_ToNNF(struct BoolExpr *);


/*
** Return an expression in disjunctive normal form.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_ToDNF(struct BoolExpr *);


/*
** Return an expression in conjunctive normal form.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_ToCNF(struct BoolExpr *);


/*
** Return a DNF expression that contains all prime implicants.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_CompleteSum(struct BoolExpr *);


/*
** Substitute a subset of support variables with other Boolean expressions.
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_Compose(struct BoolExpr *, struct BoolExprDict *var2ex);


/*
** Restrict a subset of support variables to {0, 1}
**
** NOTE: Returns a new reference.
*/
struct BoolExpr * BoolExpr_Restrict(struct BoolExpr *, struct BoolExprDict *var2const);


/* Return a new Boolean expression iterator. */
struct BoolExprIter * BoolExprIter_New(struct BoolExpr *ex);

/* Delete a Boolean expression iterator. */
void BoolExprIter_Del(struct BoolExprIter *);

/* Return the next Boolean expression in an iteration. */
struct BoolExpr * BoolExprIter_Next(struct BoolExprIter *);


/* Return a new array of Boolean expressions. */
struct BoolExprArray * BoolExprArray_New(size_t length, struct BoolExpr **items);

/* Delete an array of Boolean expressions. */
void BoolExprArray_Del(struct BoolExprArray *);

/* Return true if two arrays are equal. */
bool BoolExprArray_Equal(struct BoolExprArray *, struct BoolExprArray *);


/* Return a new 2d array of Boolean expressions. */
struct BoolExprArray2 * BoolExprArray2_New(size_t length, size_t *lengths, struct BoolExpr ***items);

/* Delete a two-dimensional array of Boolean expressions. */
void BoolExprArray2_Del(struct BoolExprArray2 *);

/* Return true if two 2d arrays are equal. */
bool BoolExprArray2_Equal(struct BoolExprArray2 *, struct BoolExprArray2 *);

/* Return the cartesian product of two 2d arrays */
struct BoolExprArray * BoolExprArray2_Product(struct BoolExprArray2 *, BoolExprType t);


/*
** Return a new vector of Boolean expressions.
**
** All items will be initialized to NULL.
*/
struct BoolExprVector * BoolExprVector_New(void);

/* Delete a vector of Boolean expressions. */
void BoolExprVector_Del(struct BoolExprVector *);

bool BoolExprVector_Insert(struct BoolExprVector *, size_t index, struct BoolExpr *ex);

bool BoolExprVector_Append(struct BoolExprVector *, struct BoolExpr *ex);


/*
** Return a new dictionary of Boolean expressions.
*/
struct BoolExprDict * BoolExprDict_New(size_t (*prehash)(struct BoolExpr *));

/* Return a mapping from variables to arbitrary expressions. */
struct BoolExprDict * BoolExprVarMap_New(void);

/* Return a mapping from literals to arbitrary expressions. */
struct BoolExprDict * BoolExprLitMap_New(void);

/* Delete a dictionary of Boolean expressions. */
void BoolExprDict_Del(struct BoolExprDict *);

/* Insert an expression into the dictionary. */
bool BoolExprDict_Insert(struct BoolExprDict *, struct BoolExpr *key, struct BoolExpr *val);

/* Delete an expression from the dictionary. */
bool BoolExprDict_Remove(struct BoolExprDict *, struct BoolExpr *key);

struct BoolExpr * BoolExprDict_Search(struct BoolExprDict *, struct BoolExpr *key);

bool BoolExprDict_Contains(struct BoolExprDict *, struct BoolExpr *key);


/*
** Return a new set of Boolean expressions.
*/
struct BoolExprSet * BoolExprSet_New(size_t (*prehash)(struct BoolExpr *));

/* Return a set of variables */
struct BoolExprSet * BoolExprVarSet_New(void);

/* Return a set of literals */
struct BoolExprSet * BoolExprLitSet_New(void);

void BoolExprSet_Del(struct BoolExprSet *);

bool BoolExprSet_Insert(struct BoolExprSet *, struct BoolExpr *key);

bool BoolExprSet_Remove(struct BoolExprSet *, struct BoolExpr *key);

bool BoolExprSet_Contains(struct BoolExprSet *, struct BoolExpr *key);


#ifdef __cplusplus
}
#endif


#endif /* BOOLEXPR_H */

