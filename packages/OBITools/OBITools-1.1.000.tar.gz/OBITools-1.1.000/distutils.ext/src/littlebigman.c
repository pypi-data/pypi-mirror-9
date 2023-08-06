/*
 * littlebigman.c
 *
 *  Created on: 11 juil. 2012
 *      Author: coissac
 */

#include<stdio.h>

int main(int argc, char *argv[])
{
    union { int entier;
            char caractere[4] ;
    } test;

    test.entier=0x01020304;

    if (test.caractere[3] == 1)
       printf("-DLITTLE_END");
    else
        printf("-DBIG_END");

	return 0;
}
