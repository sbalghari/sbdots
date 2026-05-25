// sbdots actions client

#include <cstddef>
#include <cstdlib>
#include <iostream>
#include <string>
#include <cstring>
#include <sys/socket.h>
#include <sys/un.h>
#include <filesystem>
#include <unistd.h>


// Receive loop
int recv_loop(int sock) {
    std::string buffer;
    char chunk[4096];

    while (true) {
        ssize_t bytes = recv(sock, chunk, sizeof(chunk) - 1, 0);

        if (bytes <= 0) {
            break; // connection closed or error
        }

        chunk[bytes] = '\0';
        buffer += chunk;

        size_t pos;
        while ((pos = buffer.find('\n')) != std::string::npos) {
            std::string line = buffer.substr(0, pos);
            buffer.erase(0, pos + 1);

            if (!line.empty()) {
                std::cout << line << std::endl;
                std::cout.flush();
            }
        }
    }

    close(sock);
    return 0;
}

// Send request
int send_req(int sock, std::string command) {
    command += "\n";
    if (send(sock, command.c_str(), command.size(), 0) < 0) {
        std::cerr << "ERROR: Failed to send data\n";
        close(sock);
        return 1;
    }
    return 0;
}

// Create socket
int conn_sock(int sock, const char* socket_path) {
    sockaddr_un addr;
    memset(&addr, 0, sizeof(sockaddr_un));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);

    // Connect
    if (connect(sock, (sockaddr*)&addr, sizeof(sockaddr_un)) < 0) {
        std::cerr << "ERROR: Failed to connect to socket\n";
        close(sock);
        return 1;
    }
    return 0;
}

// Source - https://stackoverflow.com/a/63360252
// Posted by einpoklum, modified by community. See post 'Timeline' for change history
// Retrieved 2026-05-25, License - CC BY-SA 4.0
inline char* get_env(const char* key) {
    if (key == nullptr) {
        throw std::invalid_argument("Null pointer passed as environment variable name");
    }
    if (*key == '\0') {
        throw std::invalid_argument("Value requested for the empty-name environment variable");
    }
    char* ev_val = getenv(key);
    if (ev_val == nullptr) {
        throw std::runtime_error("Environment variable not defined");
    }
    return ev_val;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        std::cerr << "Too few args\n";
        return 1;
    }

    std::string action = argv[1];
    std::string action_args;
    for (int i = 2; i < argc; i++) {
        action_args += argv[i];
        if (i != argc - 1) action_args += " ";
    }
    std::string command = action + " " + action_args;

    std::string socket_path;
    try {
        std::string runtime_dir = get_env("XDG_RUNTIME_DIR");
        socket_path = runtime_dir + "/sbdots-actions.sock";
    }
    catch (std::invalid_argument) {
        std::cerr << "WARNING: Falling back to temp socket path";
        socket_path = "/tmp/sbdots-actions.sock";
    }

    if (!std::filesystem::exists(socket_path)) {
        std::cerr << socket_path << " not found, make sure actions daemon is running";
        return 1;
    }
    
    int sock, conn_sock_rc, send_req_rc;
    try {
        sock = socket(AF_UNIX, SOCK_STREAM, 0);
        if (sock < 0) return 1;
        
        conn_sock_rc = conn_sock(sock, socket_path.c_str());
        if (conn_sock_rc != 0) return 1;
        
        send_req_rc = send_req(sock, command);
        if (send_req_rc != 0) return 1;

        return recv_loop(sock);
    }
    catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
    }
}