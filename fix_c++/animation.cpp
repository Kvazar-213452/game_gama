#include "animation.hpp"
#include <iostream> // Додано для std::cerr

bool Animation::loadFromFile(const std::string& filename, int count, float duration) {
    if (!texture.loadFromFile(filename)) {
        std::cerr << "Failed to load texture: " << filename << std::endl;
        return false;
    }
    
    frameCount = count;
    frameDuration = duration;
    frameSize = {
        static_cast<int>(texture.getSize().x) / frameCount,
        static_cast<int>(texture.getSize().y)
    };
    
    frames.clear();
    for (int i = 0; i < frameCount; ++i) {
        frames.emplace_back(i * frameSize.x, 0, frameSize.x, frameSize.y);
    }
    
    return true;
}

void Animation::createPlaceholder(int count, const sf::Vector2i& size) {
    frameCount = count;
    frameDuration = 0.1f;
    frameSize = size;
    
    sf::Image img;
    img.create(size.x * count, size.y, sf::Color::Transparent);
    
    for (int i = 0; i < count; ++i) {
        int offset = i * size.x;
        for (int x = 0; x < size.x; ++x) {
            img.setPixel(offset + x, x % size.y, sf::Color::Red);
            img.setPixel(offset + x, size.y - 1 - (x % size.y), sf::Color::Red);
        }
    }
    
    texture.loadFromImage(img);
    
    frames.clear();
    for (int i = 0; i < frameCount; ++i) {
        frames.emplace_back(i * frameSize.x, 0, frameSize.x, frameSize.y);
    }
}

AnimationSystem::AnimationSystem() : frameSize(50, 50) {
    animations = {
        {"idle", {}}, {"walk", {}}, {"jump", {}}, 
        {"attack", {}}, {"hurt", {}}, {"death", {}}, {"jerk", {}}
    };
}

void AnimationSystem::setSkin(const std::string& skin) {
    std::string basePath = "assets/" + skin;
    
    if (!fs::exists(basePath)) {
        std::cerr << "Шлях до скіна не знайдено: " << basePath << std::endl;
        createPlaceholders();
        return;
    }
    
    std::map<std::string, std::string> animationFiles = {
        {"idle", "Idle.png"},
        {"walk", "Run.png"},
        {"jump", "Jump.png"},
        {"attack", "Attack2.png"},
        {"hurt", "Hurt.png"},
        {"death", "Death.png"},
        {"jerk", "Squat.png"}
    };
    
    std::map<std::string, int> frameCounts = {
        {"idle", 4}, {"walk", 6}, {"jump", 8},
        {"attack", 6}, {"hurt", 4}, {"death", 8}, {"jerk", 4}
    };
    
    for (auto& [state, anim] : animations) {
        std::string filename = animationFiles[state];
        std::string filepath = basePath + "/" + filename;
        int count = frameCounts[state];
        
        if (!fs::exists(filepath)) {
            std::cerr << "Попередження: файл " << filename 
                      << " не знайдено для скіна " << skin << std::endl;
            anim.createPlaceholder(count, frameSize);
        } else {
            anim.loadFromFile(filepath, count, 0.1f);
        }
    }
}

void AnimationSystem::createPlaceholders() {
    for (auto& [state, anim] : animations) {
        int count = 4;
        if (state == "walk") count = 6;
        else if (state == "jump" || state == "death") count = 8;
        else if (state == "attack") count = 6;
        
        anim.createPlaceholder(count, frameSize);
    }
}

Animation& AnimationSystem::getAnimation(const std::string& state) {
    return animations.at(state);
}

const sf::Vector2i& AnimationSystem::getFrameSize() const {
    return frameSize;
}