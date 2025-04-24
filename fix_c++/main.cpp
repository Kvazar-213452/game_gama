#include "animation.hpp"
#include "player.hpp"
#include <SFML/Network.hpp>
#include <iostream>
#include <vector>
#include <algorithm>

const unsigned short PORT = 55001;
const std::string SERVER_IP = "26.102.24.118";

// Константи для резинової оболонки
const float TARGET_WIDTH = 800.f;
const float TARGET_HEIGHT = 600.f;
const float ASPECT_RATIO = TARGET_WIDTH / TARGET_HEIGHT;

int main() {
    // Connect to server
    sf::TcpSocket socket;
    if (socket.connect(SERVER_IP, PORT) != sf::Socket::Done) {
        std::cerr << "Failed to connect to server" << std::endl;
        return 1;
    }
    
    // Receive player ID
    sf::Packet idPacket;
    if (socket.receive(idPacket) != sf::Socket::Done) {
        std::cerr << "Failed to receive player ID" << std::endl;
        return 1;
    }
    
    int playerId;
    idPacket >> playerId;
    std::cout << "Connected as player " << playerId << std::endl;
    
    // Create window
    sf::RenderWindow window(sf::VideoMode(800, 600), "SFML Platformer", sf::Style::Default);
    window.setFramerateLimit(60);
    
    // Create view (camera)
    sf::View view(sf::FloatRect(0, 0, TARGET_WIDTH, TARGET_HEIGHT));
    
    // Create platform
    sf::RectangleShape platform(sf::Vector2f(800, 50));
    platform.setPosition(0, 450);
    platform.setFillColor(sf::Color::Green);
    
    // Load animations
    AnimationSystem animations;
    animations.setSkin("eblan");
    
    // Game state
    std::vector<Player> players;
    bool leftPressed = false;
    bool rightPressed = false;
    bool jumpPressed = false;
    bool jumpJustPressed = false;
    
    sf::Clock clock;
    while (window.isOpen()) {
        float deltaTime = clock.restart().asSeconds();
        
        // Handle window resize
        sf::Event event;
        while (window.pollEvent(event)) {
            if (event.type == sf::Event::Closed) {
                window.close();
            }
            else if (event.type == sf::Event::Resized) {
                // Оновлюємо viewport для підтримки співвідношення сторін
                float windowAspectRatio = static_cast<float>(event.size.width) / event.size.height;
                float viewportWidth = 1.f;
                float viewportHeight = 1.f;
                float viewportX = 0.f;
                float viewportY = 0.f;

                if (windowAspectRatio > ASPECT_RATIO) {
                    // Широке вікно - додаємо чорні смуги з боків
                    viewportWidth = ASPECT_RATIO / windowAspectRatio;
                    viewportX = (1.f - viewportWidth) / 2.f;
                }
                else {
                    // Високе вікно - додаємо чорні смуги зверху та знизу
                    viewportHeight = windowAspectRatio / ASPECT_RATIO;
                    viewportY = (1.f - viewportHeight) / 2.f;
                }

                view.setViewport(sf::FloatRect(viewportX, viewportY, viewportWidth, viewportHeight));
            }
            
            // Handle input
            if (event.type == sf::Event::KeyPressed) {
                if (event.key.code == sf::Keyboard::Left) leftPressed = true;
                if (event.key.code == sf::Keyboard::Right) rightPressed = true;
                if (event.key.code == sf::Keyboard::Up || event.key.code == sf::Keyboard::Space) {
                    if (!jumpPressed) jumpJustPressed = true;
                    jumpPressed = true;
                }
            }
            
            if (event.type == sf::Event::KeyReleased) {
                if (event.key.code == sf::Keyboard::Left) leftPressed = false;
                if (event.key.code == sf::Keyboard::Right) rightPressed = false;
                if (event.key.code == sf::Keyboard::Up || event.key.code == sf::Keyboard::Space) {
                    jumpPressed = false;
                    jumpJustPressed = false;
                }
            }
        }
        
        // Send input to server
        sf::Packet inputPacket;
        inputPacket << leftPressed << rightPressed << jumpJustPressed;
        jumpJustPressed = false;
        
        if (socket.send(inputPacket) != sf::Socket::Done) {
            std::cerr << "Failed to send input to server" << std::endl;
            break;
        }
        
        // Receive game state from server
        sf::Packet statePacket;
        if (socket.receive(statePacket) != sf::Socket::Done) {
            std::cerr << "Failed to receive game state" << std::endl;
            break;
        }
        
        int playerCount;
        statePacket >> playerCount;
        
        std::vector<int> receivedIds;
        for (int i = 0; i < playerCount; i++) {
            int id;
            float x, y;
            bool isMoving, isJumping;
            int direction;
            
            statePacket >> id >> x >> y >> isMoving >> isJumping >> direction;
            receivedIds.push_back(id);
            
            auto it = std::find_if(players.begin(), players.end(), 
                [id](const Player& p) { return p.id == id; });
            
            if (it == players.end()) {
                Player newPlayer;
                newPlayer.id = id;
                newPlayer.isLocal = (id == playerId);
                newPlayer.sprite.setPosition(x, y);
                newPlayer.currentState = "idle";
                newPlayer.animationTime = 0;
                newPlayer.currentFrame = 0;
                
                players.push_back(newPlayer);
                it = players.end() - 1;
            }
            
            it->position = sf::Vector2f(x, y);
            it->isMoving = isMoving;
            it->isJumping = isJumping;
            it->direction = direction;
            it->sprite.setPosition(x, y);
            
            // Update animation
            it->updateAnimation(deltaTime, animations);
            
            if (it->isLocal) {
                view.setCenter(it->position.x, 300);
            }
        }
        
        // Remove disconnected players
        players.erase(std::remove_if(players.begin(), players.end(), 
            [&receivedIds](const Player& p) {
                return std::find(receivedIds.begin(), receivedIds.end(), p.id) == receivedIds.end();
            }), players.end());
        
        // Draw everything
        window.clear();
        window.setView(view);
        
        platform.setPosition(view.getCenter().x - view.getSize().x/2, 450);
        window.draw(platform);
        
        for (const auto& player : players) {
            window.draw(player.sprite);
        }
        
        window.display();
    }
    
    return 0;
}