#pragma once
#include <SFML/Graphics.hpp>
#include <string>

struct Player {
    sf::Vector2f position;
    int id;
    bool isLocal;
    bool isMoving;
    bool isJumping;
    int direction;
    
    std::string currentState;
    float animationTime;
    int currentFrame;
    
    sf::Sprite sprite;
    
    void updateAnimation(float deltaTime, class AnimationSystem& animSystem);
};