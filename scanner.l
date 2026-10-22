%{
#include <stdio.h>
#include <string.h>
#include "symtable.h"

int line_num = 1;
%}

%option noyywrap

WORD        [a-zA-Z][a-zA-Z0-9_]*
NUMBER      0|[1-9][0-9]*
WHITESPACE  [ \t\r]+
NEWLINE     \n

%%

"sensor_node"|"signal"|"buffer"|"detect"|"otherwise"|"monitor"|"sample"|"emit" { 
    printf("%-15s | -1\n", yytext); 
}

"=="|"!="|"<="|">="|"<"|">"|"+"|"-"|"*"|"/"|"%"|"=" { 
    printf("%-15s | -1\n", yytext); 
}

";"|","|"("|")"|"{"|"}"|"["|"]" { 
    printf("%-15s | -1\n", yytext); 
}

{NUMBER} {
    int pos = addToST(yytext);
    printf("const %-9s | %d\n", yytext, pos);
}

{WORD} {
    int pos = addToST(yytext);
    printf("id %-12s | %d\n", yytext, pos);
}

[0-9]+[a-zA-Z_]+[a-zA-Z0-9_]* { 
    printf("Lexical error at line %d: invalid token '%s'\n", line_num, yytext); 
}

{WHITESPACE} { /* ignore */ }
{NEWLINE}    { line_num++; }
.            { printf("Lexical error at line %d: unrecognized char '%s'\n", line_num, yytext); }

%%

int main(int argc, char **argv) {
    if (argc > 1) {
        yyin = fopen(argv[1], "r");
        if (!yyin) {
            printf("Error opening file %s\n", argv[1]);
            return 1;
        }
    }
    
    printf("%-15s | ST Position\n", "Token");
    printf("----------------------------------------\n");
    
    yylex();
    printST();
    
    return 0;
}