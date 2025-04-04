package main

import (
	"fmt"
	"head/src"
	"html/template"
	"net/http"
	"os/exec"
)

func main() {
	var cmd *exec.Cmd
	cmd = src.Start_shell(8080, "/")

	http.Handle("/static/", http.StripPrefix("/static/", http.FileServer(http.Dir("static"))))

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		tmpl, err := template.ParseFiles("templates/index.html")
		if err != nil {
			http.Error(w, "Error loading template", http.StatusInternalServerError)
			return
		}
		tmpl.Execute(w, nil)
	})

	http.HandleFunc("/submit", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodPost {
			http.Error(w, "Invalid request method", http.StatusMethodNotAllowed)
			return
		}

		r.ParseForm()
		data := r.FormValue("code")
		fmt.Println("Received code:", data)
		w.Write([]byte("Data received successfully"))
	})

	port := ":8080"
	fmt.Println("Server is running on http://localhost" + port)
	http.ListenAndServe(port, nil)

	if err := cmd.Process.Kill(); err != nil {
		fmt.Printf("not shell_web.exe: %v\n", err)
	}
}
