#pragma once
#include <SFML/Graphics.hpp>
#include <map>
#include <vector>
#include <string>
#include <filesystem>
#include <iostream> // Додано для std::cerr

namespace fs = std::filesystem;

struct Animation {
    sf::Texture texture;
    std::vector<sf::IntRect> frames;
    int frameCount;
    float frameDuration;
    sf::Vector2i frameSize;
    
    bool loadFromFile(const std::string& filename, int count, float duration);
    void createPlaceholder(int count, const sf::Vector2i& size);
};

class AnimationSystem {
private:
    std::map<std::string, Animation> animations;
    sf::Vector2i frameSize;
    
    void createPlaceholders();

public:
    AnimationSystem();
    void setSkin(const std::string& skin);
    Animation& getAnimation(const std::string& state);
    const sf::Vector2i& getFrameSize() const;
};