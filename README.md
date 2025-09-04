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
pip install PyOpenGL PyOpenGL_accelerate
```

### Alternative Installation
If you encounter issues with the above command, try:

```bash
pip install PyOpenGL==3.1.5
pip install PyOpenGL_accelerate==3.1.5
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

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python Version**: Python 3.7 or higher
- **Graphics**: OpenGL 2.1 compatible graphics card
- **Memory**: 4 GB RAM
- **Storage**: 100 MB available space

### Recommended Requirements
- **Operating System**: Windows 11, macOS 12+, or Linux (Ubuntu 20.04+)
- **Python Version**: Python 3.9 or higher
- **Graphics**: Dedicated graphics card with OpenGL 3.3+ support
- **Memory**: 8 GB RAM
- **Storage**: 200 MB available space
- **Display**: 1920x1080 resolution or higher

### Performance Notes
- The game targets 60 FPS for optimal gameplay experience
- Lower-end systems may experience reduced frame rates during intense combat scenes
- Graphics settings are automatically optimized based on system capabilities

## Known Issues and Troubleshooting

### Common Issues

#### 1. PyOpenGL Installation Problems
**Problem**: `ImportError: No module named 'OpenGL'`

**Solutions**:
- Ensure pip is up to date: `pip install --upgrade pip`
- Try alternative installation: `pip install PyOpenGL-accelerate`
- On Windows, install Visual C++ Redistributable
- On macOS, install Xcode command line tools: `xcode-select --install`
- On Linux, install development packages: `sudo apt-get install python3-opengl`

#### 2. Graphics Performance Issues
**Problem**: Low frame rate or stuttering gameplay

**Solutions**:
- Update graphics drivers to the latest version
- Close other graphics-intensive applications
- Enable cheat mode (C key) for testing without performance constraints
- Reduce window size if running in windowed mode

#### 3. Window Display Problems
**Problem**: Game window doesn't appear or appears corrupted

**Solutions**:
- Check if multiple monitors are connected and try different display settings
- Verify OpenGL support: Run `python -c "from OpenGL import GL; print(GL.glGetString(GL.GL_VERSION))"`
- Update or reinstall graphics drivers
- Try running with administrator privileges (Windows)

#### 4. Input Lag or Unresponsive Controls
**Problem**: Delayed response to keyboard/mouse input

**Solutions**:
- Ensure the game window has focus (click on it)
- Check for background applications consuming CPU resources
- Restart the game if controls become unresponsive
- Verify keyboard layout settings

#### 5. Audio Issues
**Problem**: No sound effects (Note: This game currently focuses on visual experience)

**Solutions**:
- The current version is primarily a visual experience
- Sound effects may be added in future updates
- Focus on visual feedback for game events

### Advanced Troubleshooting

#### Debug Mode
To enable additional debugging information:
1. Open `main.py` in a text editor
2. Look for debug flags or add print statements for troubleshooting
3. Monitor console output for error messages

#### System Compatibility
- **Windows**: Tested on Windows 10/11 with various graphics cards
- **macOS**: Compatible with Intel and Apple Silicon Macs
- **Linux**: Tested on Ubuntu, may require additional OpenGL libraries

#### Performance Optimization
- The game includes frame rate limiting to maintain consistent performance
- Explosion effects and particle systems are optimized for smooth gameplay
- Large numbers of enemies may impact performance on older systems

### Getting Help

If you encounter issues not covered in this troubleshooting section:
1. Check the console output for specific error messages
2. Verify all dependencies are correctly installed
3. Ensure your system meets the minimum requirements
4. Try running the game in different compatibility modes

### Development Notes

- The game uses custom OpenGL rendering for optimal performance
- All 3D models are procedurally generated using mathematical functions
- The physics system is custom-built for tactical combat mechanics
- Frame rate is capped at 60 FPS for consistent gameplay experience

---

**Enjoy your tactical combat experience in 3D Combat Arena!**

*For the best gaming experience, ensure your system meets the recommended requirements and all dependencies are properly installed.*