/*
** Filename: array2.c
*/


#include <stdbool.h>
#include <stddef.h>
#include <stdlib.h>

#include "boolexpr.h"


/* boolexpr.c */
struct BoolExpr * _opn_new(BoolExprType t, size_t n, ...);


struct BoolExprArray2 *
BoolExprArray2_New(size_t length, size_t *lengths, struct BoolExpr ***items)
{
    struct BoolExprArray2 *array2;

    array2 = (struct BoolExprArray2 *) malloc(sizeof(struct BoolExprArray2));
    if (array2 == NULL)
        return NULL; // LCOV_EXCL_LINE

    array2->items = (struct BoolExprArray **) malloc(length * sizeof(struct BoolExprArray *));
    if (array2->items == NULL) {
        free(array2); // LCOV_EXCL_LINE
        return NULL;  // LCOV_EXCL_LINE
    }

    array2->length = length;

    for (size_t i = 0; i < length; ++i)
        array2->items[i] = BoolExprArray_New(lengths[i], items[i]);

    return array2;
}


void
BoolExprArray2_Del(struct BoolExprArray2 *array2)
{
    for (size_t i = 0; i < array2->length; ++i)
        BoolExprArray_Del(array2->items[i]);

    free(array2->items);
    free(array2);
}


bool
BoolExprArray2_Equal(struct BoolExprArray2 *self, struct BoolExprArray2 *other)
{
    if (self->length != other->length)
        return false;

    for (size_t i = 0; i < self->length; ++i)
        if (!BoolExprArray_Equal(self->items[i], other->items[i]))
            return false;

    return true;
}


static struct BoolExprArray *
_multiply(struct BoolExprArray *a, struct BoolExprArray *b, BoolExprType t)
{
    size_t length = a->length * b->length;
    struct BoolExpr **items;
    struct BoolExprArray *prod;

    items = (struct BoolExpr **) malloc(length * sizeof(struct BoolExpr *));
    if (items == NULL)
        return NULL; // LCOV_EXCL_LINE

    for (size_t i = 0, index = 0; i < a->length; ++i) {
        for (size_t j = 0; j < b->length; ++j, ++index) {
            items[index] = _opn_new(t, 2, a->items[i], b->items[j]);
            if (items[index] == NULL) {
                /* LCOV_EXCL_START */
                for (size_t k = 0; k < index; ++k)
                    BoolExpr_DecRef(items[k]);
                free(items);
                return NULL;
                /* LCOV_EXCL_STOP */
            }
        }
    }

    prod = BoolExprArray_New(length, items);

    for (size_t i = 0; i < length; ++i)
        BoolExpr_DecRef(items[i]);
    free(items);

    return prod;
}


static struct BoolExprArray *
_product(struct BoolExprArray2 *array2, BoolExprType t, size_t n)
{
    if (n == 0) {
        struct BoolExpr *items[] = {IDENTITY[t]};
        return BoolExprArray_New(1, items);
    }
    else {
        struct BoolExprArray *prev;
        struct BoolExprArray *prod;

        prev = _product(array2, t, n-1);
        if (prev == NULL)
            return NULL; // LCOV_EXCL_LINE

        prod = _multiply(array2->items[n-1], prev, t);

        BoolExprArray_Del(prev);

        return prod;
    }
}


struct BoolExprArray *
BoolExprArray2_Product(struct BoolExprArray2 *self, BoolExprType t)
{
    return _product(self, t, self->length);
}

