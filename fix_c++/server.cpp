#include <SFML/Network.hpp>
#include <iostream>
#include <vector>
#include <thread>

const unsigned short PORT = 55001;
const std::string SERVER_IP = "26.102.24.118";  // Додана IP-адреса сервера
const float GRAVITY = 0.5f;
const float JUMP_FORCE = -12.0f;
const float MOVE_SPEED = 5.0f;

struct Player {
    sf::Vector2f position;
    sf::Vector2f velocity;
    bool isJumping;
    bool canDoubleJump;
    bool isMoving;
    int id;
    int direction; // 1 - right, -1 - left
};

std::vector<Player> players;
sf::Mutex playersMutex;

void handleClient(sf::TcpSocket* socket) {
    int playerId = -1;
    
    // Assign ID to the player
    {
        sf::Lock lock(playersMutex);
        players.push_back(Player{
            sf::Vector2f(100 + players.size() * 50, 100), 
            sf::Vector2f(0, 0), 
            false, 
            true,
            false,
            static_cast<int>(players.size()),
            1
        });
        playerId = players.back().id;
        
        // Send player their ID
        sf::Packet idPacket;
        idPacket << playerId;
        socket->send(idPacket);
    }
    
    std::cout << "Player " << playerId << " connected from " << socket->getRemoteAddress() << std::endl;
    
    while (true) {
        // Receive input from client
        sf::Packet inputPacket;
        if (socket->receive(inputPacket) != sf::Socket::Done) {
            break;
        }
        
        bool left, right, jump;
        inputPacket >> left >> right >> jump;
        
        // Update player state
        {
            sf::Lock lock(playersMutex);
            for (auto& player : players) {
                if (player.id == playerId) {
                    // Handle input
                    player.velocity.x = 0;
                    player.isMoving = false;
                    
                    if (left) {
                        player.velocity.x = -MOVE_SPEED;
                        player.isMoving = true;
                        player.direction = -1;
                    }
                    if (right) {
                        player.velocity.x = MOVE_SPEED;
                        player.isMoving = true;
                        player.direction = 1;
                    }
                    
                    // Handle jumping
                    if (jump) {
                        if (!player.isJumping) {
                            player.velocity.y = JUMP_FORCE;
                            player.isJumping = true;
                            player.canDoubleJump = true;
                        } 
                        else if (player.canDoubleJump) {
                            player.velocity.y = JUMP_FORCE * 0.8f;
                            player.canDoubleJump = false;
                        }
                    }
                    
                    // Apply gravity
                    player.velocity.y += GRAVITY;
                    
                    // Update position
                    player.position += player.velocity;
                    
                    // Ground collision (platform at y=400)
                    if (player.position.y > 400) {
                        player.position.y = 400;
                        player.velocity.y = 0;
                        player.isJumping = false;
                        player.canDoubleJump = true;
                    }
                    
                    break;
                }
            }
        }
        
        // Send game state to client
        sf::Packet statePacket;
        {
            sf::Lock lock(playersMutex);
            statePacket << static_cast<int>(players.size());
            for (const auto& player : players) {
                statePacket << player.id << player.position.x << player.position.y 
                          << player.isMoving << player.isJumping << player.direction;
            }
        }
        
        if (socket->send(statePacket) != sf::Socket::Done) {
            break;
        }
    }
    
    // Remove player on disconnect
    {
        sf::Lock lock(playersMutex);
        players.erase(std::remove_if(players.begin(), players.end(), 
            [playerId](const Player& p) { return p.id == playerId; }), players.end());
    }
    
    std::cout << "Player " << playerId << " disconnected\n";
    delete socket;
}

int main() {
    sf::TcpListener listener;
    
    // Спроба прив'язатися до конкретної IP-адреси
    if (listener.listen(PORT, SERVER_IP) != sf::Socket::Done) {
        std::cerr << "Failed to listen on " << SERVER_IP << ":" << PORT << std::endl;
        std::cerr << "Trying to listen on all available interfaces..." << std::endl;
        
        // Якщо не вдалося прив'язатися до конкретної IP, спробуємо всі інтерфейси
        if (listener.listen(PORT) != sf::Socket::Done) {
            std::cerr << "Failed to listen on port " << PORT << std::endl;
            return 1;
        }
    }
    
    std::cout << "Server started on " << SERVER_IP << ":" << PORT << std::endl;
    
    while (true) {
        sf::TcpSocket* socket = new sf::TcpSocket;
        if (listener.accept(*socket) == sf::Socket::Done) {
            std::thread clientThread(handleClient, socket);
            clientThread.detach();
        } else {
            delete socket;
        }
    }
    
    return 0;
}