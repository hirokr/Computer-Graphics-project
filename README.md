# 3D Combat Arena

## Game Description

**3D Combat Arena** is an immersive 3D tactical shooter game built with OpenGL and Python. Players navigate a grid-based battlefield, engaging in intense combat against AI enemies while utilizing cover systems, power-ups, and strategic positioning. The game features realistic 3D graphics, dynamic lighting effects, explosion systems, and multiple camera perspectives for an engaging combat experience.

### Key Highlights
- **3D OpenGL Graphics**: Fully rendered 3D environment with custom sphere rendering and humanoid character models
- **Tactical Combat**: Strategic gameplay with cover systems, crouching mechanics, and line-of-sight detection
- **Dynamic Systems**: Real-time explosion effects, particle systems, and coordinated enemy attacks
- **Multiple Game Modes**: Standard gameplay and cheat mode for testing and exploration
- **Power-Up System**: Collectible items that enhance player abilities (health, speed, damage, shield, bullets)

## Installation Instructions

### Prerequisites
Ensure you have Python 3.7 or higher installed on your system.

### Required Dependencies
Install the following Python packages using pip:

```bash
pip install PyOpenGL
```

### Alternative Installation
If you encounter issues with the above command, try:

```bash
pip install PyOpenGL==3.1.5
```

### Running the Game
1. Navigate to the project directory
2. Run the main game file:
   ```bash
   python main.py
   ```

## Game Controls and Mechanics

### Movement Controls
- **W** - Move forward
- **S** - Move backward  
- **Q** - Strafe left
- **E** - Strafe right
- **A/D** - Aim gun left/right (or move left/right in cheat mode)
- **Z/X** - Rotate player body left/right
- **Ctrl+Q** - Crouch/lie down for cover
- **F** - Rotate avatar face

### Combat Controls
- **Left Click** - Fire weapon
- **Right Click** - Toggle camera view (first-person/third-person)

### Camera Controls
- **Arrow Keys** - Move/rotate camera when in free camera mode
  - **Up/Down Arrows** - Move camera up/down
  - **Left/Right Arrows** - Rotate camera left/right

### Special Controls
- **C** - Toggle cheat mode (unlimited bullets, enhanced movement)
- **R** - Restart/reset game

### Combat Mechanics
- **Cover System**: Use walls and obstacles to hide from enemy fire
- **Crouching**: Reduces detection radius and provides tactical advantage
- **Line of Sight**: Enemies can only detect and shoot at visible targets
- **Bullet Physics**: Realistic projectile trajectories and collision detection
- **Health System**: Player starts with 5 lives, loses life when hit by enemy projectiles

## Features and Gameplay Overview

### Core Gameplay
- **Objective**: Survive waves of enemies while maintaining ammunition and health
- **Grid-Based Movement**: Navigate a structured battlefield with strategic positioning
- **Enemy AI**: Intelligent enemies that seek cover, coordinate attacks, and adapt to player behavior
- **Countdown Timer**: 30-second survival challenges with bonus time for enemy eliminations

### Power-Up System
Collect heart-shaped power-ups that provide various enhancements:
- **Health (Green)**: Restores player health
- **Speed (Blue)**: Increases movement speed
- **Damage (Red)**: Enhances weapon damage
- **Shield (Yellow)**: Provides temporary protection
- **Bullets (Orange)**: Replenishes ammunition

### Advanced Features
- **Bomb System**: Destructible bombs that can be triggered by gunfire
- **Explosion Effects**: Dynamic particle systems with screen shake effects
- **Coordinated Attacks**: Enemies execute synchronized assault patterns
- **Avatar System**: Interactive NPC with face rotation animations
- **Cover Destruction**: Destructible environment elements
- **Multiple Camera Modes**: Switch between first-person and third-person perspectives

### Visual Effects
- **3D Humanoid Models**: Detailed player and enemy character models
- **Particle Systems**: Explosion effects, muzzle flashes, and environmental particles
- **Dynamic Lighting**: Real-time lighting effects and shadows
- **Screen Shake**: Immersive feedback during explosions and impacts
- **Smooth Animations**: Fluid character movements and rotations

### Game Statistics
- **Score Tracking**: Points awarded for enemy eliminations
- **Accuracy Monitoring**: Tracks bullets fired vs. hits
- **Survival Timer**: Real-time countdown with bonus time mechanics
- **Performance Metrics**: FPS counter and frame rate optimization

**Enjoy your tactical combat experience in 3D Combat Arena!**

*For the best gaming experience, ensure your system meets the recommended requirements and all dependencies are properly installed.*
