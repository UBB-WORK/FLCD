#include "symtable.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define TABLE_SIZE 100

typedef struct Node {
    char key[50];
    struct Node* next;
} Node;

Node* hashTable[TABLE_SIZE] = {NULL};

int hashFunction(char* key) {
    int sum = 0;
    for (int i = 0; i < strlen(key); i++) {
        sum += key[i];
    }
    return sum % TABLE_SIZE;
}

int addToST(char* key) {
    int idx = hashFunction(key);
    Node* current = hashTable[idx];
    Node* prev = NULL;

    // Check if the token already exists in this bucket
    while (current != NULL) {
        if (strcmp(current->key, key) == 0) return idx;
        prev = current;
        current = current->next;
    }

    // Insert new token at the tail
    Node* newNode = (Node*)malloc(sizeof(Node));
    strcpy(newNode->key, key);
    newNode->next = NULL;

    if (prev == NULL) {
        hashTable[idx] = newNode;
    } else {
        prev->next = newNode;
    }

    return idx;  // Return the bucket index for the PIF
}

void printST() {
    printf("\nSymbol Table (Hash Table)\n");
    printf("Bucket   | Elements\n");
    printf("----------------------------------------\n");
    for (int i = 0; i < TABLE_SIZE; i++) {
        if (hashTable[i] != NULL) {
            printf("%-8d | ", i);
            Node* current = hashTable[i];
            while (current != NULL) {
                printf("%s -> ", current->key);
                current = current->next;
            }
            printf("NULL\n");
        }
    }
}

// Din automat in gramatica (option 1) 1) FA => RG