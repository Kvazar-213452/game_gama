#include "player.hpp"
#include "animation.hpp"

void Player::updateAnimation(float deltaTime, AnimationSystem& animSystem) {
    // Determine state
    if (isJumping) {
        currentState = "jump";
    } 
    else if (isMoving) {
        currentState = "walk";
    } 
    else {
        currentState = "idle";
    }
    
    auto& anim = animSystem.getAnimation(currentState);
    
    // Update animation
    animationTime += deltaTime;
    if (animationTime >= anim.frameDuration) {
        animationTime = 0;
        currentFrame = (currentFrame + 1) % anim.frameCount;
    }
    
    sprite.setTexture(anim.texture);
    sprite.setTextureRect(anim.frames[currentFrame]);
    
    // Flip sprite based on direction
    if (direction == -1) {
        sprite.setScale(-1.f, 1.f);
        sprite.setOrigin(animSystem.getFrameSize().x, 0);
    } else {
        sprite.setScale(1.f, 1.f);
        sprite.setOrigin(0, 0);
    }
}