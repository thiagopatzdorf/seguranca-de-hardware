/* Copia de string: a forma insegura e a forma segura, lado a lado.
 *
 * Em C, `strcpy` copia ate achar um '\0', sem olhar o tamanho do destino:
 * se a origem for maior, escreve alem do buffer. Este programa NAO explora
 * isso; ele mostra como escrever de forma que o estouro nao aconteca, e
 * deixa o compilador provar.
 *
 * Compile com as defesas ligadas (o padrao das distribuicoes hoje):
 *
 *   cc -O2 -D_FORTIFY_SOURCE=2 -fstack-protector-strong \
 *      -o strings_seguras strings_seguras.c
 *   ./strings_seguras "texto curto"
 *   ./strings_seguras "um texto propositalmente maior que o buffer de destino"
 *
 * Na entrada grande, a versao segura TRUNCA e avisa; a copia nunca passa do
 * fim do buffer. Com _FORTIFY_SOURCE, o proprio glibc recusa um `strcpy`
 * cujo tamanho ele consegue provar que estoura, abortando com mensagem em
 * vez de corromper a memoria. Veja as defesas do binario com:
 *
 *   python3 protecoes.py ./strings_seguras
 */
#include <stdio.h>
#include <string.h>

#define TAMANHO_DESTINO 16

/* Forma segura: diz o tamanho do destino, garante o terminador, avisa no corte. */
static int copiar_limitado(char *destino, size_t cap, const char *origem) {
    if (cap == 0) return -1;
    size_t n = strnlen(origem, cap - 1); /* no maximo cap-1, sobra 1 para o '\0' */
    memcpy(destino, origem, n);
    destino[n] = '\0';
    return (origem[n] != '\0'); /* 1 se teve de truncar */
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "uso: %s <texto>\n", argv[0]);
        return 2;
    }
    char destino[TAMANHO_DESTINO];
    int truncou = copiar_limitado(destino, sizeof destino, argv[1]);
    printf("copiado (%zu bytes de capacidade): \"%s\"%s\n",
           sizeof destino, destino, truncou ? "  [truncado: a origem nao cabia]" : "");
    return 0;
}
