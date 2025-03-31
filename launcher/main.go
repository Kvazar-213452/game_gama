package main

import (
	"fmt"
	"net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
	fmt.Fprintf(w, "<h1>Привіт, світ!</h1>")
}

func main() {
	http.HandleFunc("/", handler)
	fmt.Println("Сервер запущено на порту 8080...")
	http.ListenAndServe(":8080", nil)
}
