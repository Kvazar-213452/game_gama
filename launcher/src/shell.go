package src

import (
	"fmt"
	"net"
	"os"
	"os/exec"
	"os/signal"
	"strconv"
	"syscall"
)

func FindFreePort() int {
	listener, err := net.Listen("tcp", "localhost:0")
	if err != nil {
		return 0
	}
	defer listener.Close()

	addr := listener.Addr().(*net.TCPAddr)
	return addr.Port
}

func Start_shell(port int, page string) *exec.Cmd {
	originalDir, _ := os.Getwd()
	var cmd *exec.Cmd

	os.Chdir("NM1")

	htmlContent := fmt.Sprintf(`%s/`+page, strconv.Itoa(port))

	args := []string{
		"test",
		"740",
		"900",
		htmlContent,
	}

	cmd = exec.Command("./shell_web.exe", args...)

	defer func() {
		os.Chdir(originalDir)
	}()

	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	cmd.Start()
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)

	doneChan := make(chan error, 1)
	go func() {
		doneChan <- cmd.Wait()
	}()

	go func() {
		select {
		case sig := <-sigChan:
			fmt.Printf("end %v. pr\n", sig)
			os.Exit(0)
		case err := <-doneChan:
			if err != nil {
				fmt.Printf("shell_web.exe end error: %v\n", err)
			} else {
				fmt.Println("shell_web.exe end.")
			}
			os.Exit(0)
		}
	}()

	return cmd
}
