from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random

class Vector3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z
    
    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar):
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def distance_to(self, other):
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2 + (self.z - other.z)**2)
    
    def normalize(self):
        length = math.sqrt(self.x**2 + self.y**2 + self.z**2)
        if length > 0:
            return Vector3(self.x/length, self.y/length, self.z/length)
        return Vector3(0, 0, 0)
    
    def to_tuple(self):
        return (self.x, self.y, self.z)

class Bullet:
    def __init__(self, position, direction, speed=15):
        self.position = Vector3(position.x, position.y, position.z)
        self.direction = direction.normalize()
        self.speed = speed
        self.active = True
        self.size = 8
        self.damage = 25  # Damage to cover objects
    
    def update(self, cover_system=None):
        if self.active:
            self.position = self.position + (self.direction * self.speed)
            
            # Check collision with cover objects
            if cover_system and cover_system.check_projectile_collision(self.position, self.size):
                # Find which cover was hit and damage it
                for cover in cover_system.covers:
                    if cover.check_collision(self.position, self.size):
                        cover.take_damage(self.damage, self.position)
                        print(f"Bullet hit cover! Cover health: {cover.health}")
                        break
                self.active = False
                return False
            
            # Check boundary collision
            if (abs(self.position.x) > 650 or abs(self.position.y) > 650 or 
                self.position.z < 0 or self.position.z > 200):
                self.active = False
                return False
        return True
    
    def draw(self):
        if not self.active:
            return
            
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Enhanced bullet visualization with trail effect
        glColor3f(0.2, 0.2, 0.2)  # Dark gray bullet
        glutSolidCube(self.size)
        
        # Add a glowing effect
        glPushMatrix()
        glScalef(1.5, 1.5, 1.5)
        glColor4f(1.0, 1.0, 0.0, 0.3)  # Yellow glow
        glutSolidCube(self.size * 0.8)
        glPopMatrix()
        
        glPopMatrix()
        
    def check_collision_with_cover(self, cover_system):
        """Check if bullet collides with any cover object"""
        if not self.active:
            return False
            
        for cover in cover_system.covers:
            if cover.check_collision(self.position, self.size):
                cover.take_damage(self.damage, self.position)
                self.active = False
                return True
        return False

class EnemyProjectile:
    def __init__(self, position, direction, speed=8):
        self.position = Vector3(position.x, position.y, position.z)
        self.direction = direction.normalize()
        self.speed = speed
        self.size = 3
        self.life_time = 300  # frames
        self.age = 0
        
    def update(self):
        self.position = self.position + (self.direction * self.speed)
        self.age += 1
        return self.age < self.life_time
        
    def draw(self):
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor3f(1.0, 0.5, 0.0)  # Orange projectile
        glutSolidSphere(self.size, 8, 8)
        glPopMatrix()
        
    def check_collision_with_player(self, player, player_radius=15):
        # Use new humanoid collision detection if available
        if hasattr(player, 'check_collision_with_projectile'):
            return player.check_collision_with_projectile(self.position, self.size)
        else:
            # Fallback to simple radius collision
            distance = self.position.distance_to(player.position)
            return distance < (self.size + player_radius)

class AIEnemy:
    def __init__(self, position):
        self.position = Vector3(position.x, position.y, position.z)
        self.original_position = Vector3(position.x, position.y, position.z)
        self.scale = 1.0
        self.scale_direction = 1
        self.scale_time = random.uniform(0, 6.28) 
        self.radius = 15  # Adjusted for humanoid body
        
        # AI behavior properties
        self.target_position = None
        self.firing_cooldown = 0
        self.firing_interval = random.randint(60, 180)  # Random firing interval
        self.accuracy = random.uniform(0.3, 0.8)  # Random accuracy
        self.projectiles = []
        self.detection_range = 400
        self.firing_range = 350
        
        # Visual indicators
        self.is_targeting = False
        self.muzzle_flash_timer = 0
        self.targeting_indicator_time = 0
        
    def update(self, player, cover_system=None):
        # Update scale animation
        self.scale_time += 0.1
        self.scale = 0.7 + 0.3 * math.sin(self.scale_time)
        
        # Update projectiles
        self.projectiles = [p for p in self.projectiles if p.update()]
        
        # Update timers
        if self.firing_cooldown > 0:
            self.firing_cooldown -= 1
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= 1
        if self.targeting_indicator_time > 0:
            self.targeting_indicator_time -= 1
            
        # AI targeting and firing logic with cover detection
        distance_to_player = self.position.distance_to(player.position)
        
        # Apply player's detection modifier
        detection_modifier = player.get_detection_modifier()
        effective_detection_range = self.detection_range * detection_modifier
        
        # Check if player is hidden behind cover
        player_hidden = False
        if cover_system:
            player_hidden = player.is_hidden_from_enemy(self.position, cover_system)
        
        # Only detect player if within modified range and not completely hidden
        can_detect_player = (distance_to_player <= effective_detection_range and 
                           not player_hidden)
        
        if can_detect_player:
            self.target_position = player.position
            self.is_targeting = True
            self.targeting_indicator_time = 30
            
            # Reduce firing accuracy if player is crouching or using cover
            accuracy_penalty = 1.0
            if player.crouching:
                accuracy_penalty *= 0.8
            if player.hiding_behind_cover:
                accuracy_penalty *= 0.6
                
            if distance_to_player <= self.firing_range and self.firing_cooldown <= 0:
                self.fire_at_target(accuracy_penalty)
                self.firing_cooldown = self.firing_interval + random.randint(-30, 30)
        else:
            self.is_targeting = False
            
    def fire_at_target(self, accuracy_penalty=1.0):
        if self.target_position:
            # Calculate direction to target with randomized accuracy
            direction = self.target_position - self.position
            direction = direction.normalize()
            
            # Add randomization based on accuracy and penalty (lower accuracy = more spread)
            base_spread = (1.0 - self.accuracy) * 0.5
            modified_spread = base_spread / accuracy_penalty  # Lower penalty = more spread
            
            direction.x += random.uniform(-modified_spread, modified_spread)
            direction.y += random.uniform(-modified_spread, modified_spread)
            direction.z += random.uniform(-modified_spread, modified_spread)
            direction = direction.normalize()
            
            # Create projectile
            projectile_start = Vector3(self.position.x, self.position.y, self.position.z + self.radius)
            projectile = EnemyProjectile(projectile_start, direction)
            self.projectiles.append(projectile)
            
            # Visual effects
            self.muzzle_flash_timer = 10
            
            # Print firing status for debugging
            if accuracy_penalty < 1.0:
                print(f"Enemy firing with reduced accuracy: {accuracy_penalty:.2f}")
    
    def draw(self):
        # Draw humanoid enemy body
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glScalef(self.scale, self.scale, self.scale)
        
        self.draw_humanoid_enemy()
        
        glPopMatrix()
        
        # Draw targeting indicator
        if self.targeting_indicator_time > 0:
            glPushMatrix()
            glTranslatef(self.position.x, self.position.y, self.position.z + 30)
            glColor3f(1.0, 0.0, 0.0)
            glBegin(GL_LINES)
            glVertex3f(-10, 0, 0)
            glVertex3f(10, 0, 0)
            glVertex3f(0, -10, 0)
            glVertex3f(0, 10, 0)
            glEnd()
            glPopMatrix()
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw()
    
    def draw_humanoid_enemy(self):
        """Draw humanoid enemy with head, torso, arms, legs, and gun"""
        
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 20)
        if self.is_targeting:
            glColor3f(0.8, 0.4, 0.4)  # Reddish skin when targeting
        else:
            glColor3f(0.7, 0.5, 0.4)  # Normal skin color
        glutSolidSphere(8, 12, 12)
        glPopMatrix()
        
        # Torso
        glPushMatrix()
        glTranslatef(0, 0, 5)
        if self.is_targeting:
            glColor3f(0.8, 0.2, 0.2)  # Bright red shirt when targeting
        else:
            glColor3f(0.6, 0.1, 0.1)  # Dark red shirt
        glScalef(1.0, 0.6, 1.8)
        glutSolidCube(12)
        glPopMatrix()
        
        # Arms
        # Left arm
        glPushMatrix()
        glTranslatef(-10, 0, 8)
        glColor3f(0.7, 0.5, 0.4)  # Skin color
        glScalef(0.6, 0.6, 1.2)
        glutSolidCube(8)
        glPopMatrix()
        
        # Right arm (holding gun)
        glPushMatrix()
        glTranslatef(10, 0, 8)
        glColor3f(0.7, 0.5, 0.4)  # Skin color
        glScalef(0.6, 0.6, 1.2)
        glutSolidCube(8)
        glPopMatrix()
        
        # Legs
        # Left leg
        glPushMatrix()
        glTranslatef(-4, 0, -8)
        glColor3f(0.2, 0.2, 0.2)  # Dark pants
        glScalef(0.7, 0.7, 1.5)
        glutSolidCube(8)
        glPopMatrix()
        
        # Right leg
        glPushMatrix()
        glTranslatef(4, 0, -8)
        glColor3f(0.2, 0.2, 0.2)  # Dark pants
        glScalef(0.7, 0.7, 1.5)
        glutSolidCube(8)
        glPopMatrix()
        
        # Feet
        # Left foot
        glPushMatrix()
        glTranslatef(-4, 3, -15)
        glColor3f(0.1, 0.1, 0.1)  # Black boots
        glScalef(0.8, 1.2, 0.4)
        glutSolidCube(6)
        glPopMatrix()
        
        # Right foot
        glPushMatrix()
        glTranslatef(4, 3, -15)
        glColor3f(0.1, 0.1, 0.1)  # Black boots
        glScalef(0.8, 1.2, 0.4)
        glutSolidCube(6)
        glPopMatrix()
        
        # Draw enemy gun
        self.draw_enemy_gun()
    
    def draw_enemy_gun(self):
        """Draw gun held by enemy"""
        
        glPushMatrix()
        
        # Gun barrel
        glPushMatrix()
        glTranslatef(0, 20, 8)
        glRotatef(90, 1, 0, 0)
        glColor3f(0.3, 0.3, 0.3)  # Dark gray metal
        gluCylinder(gluNewQuadric(), 2, 2, 25, 12, 12)
        glPopMatrix()
        
        # Gun body/receiver
        glPushMatrix()
        glTranslatef(0, 13, 8)
        glColor3f(0.4, 0.4, 0.4)  # Gray
        glScalef(1.2, 0.8, 0.6)
        glutSolidCube(8)
        glPopMatrix()
        
        # Gun grip
        glPushMatrix()
        glTranslatef(0, 10, 3)
        glColor3f(0.2, 0.2, 0.2)  # Dark grip
        glScalef(0.8, 0.6, 1.0)
        glutSolidCube(6)
        glPopMatrix()
        
        # Muzzle flash when firing
        if self.muzzle_flash_timer > 0:
            glPushMatrix()
            glTranslatef(0, 25, 8)
            glColor3f(1.0, 1.0, 0.0)  # Yellow flash
            glutSolidSphere(3, 8, 8)
            glPopMatrix()
        
        glPopMatrix()
    
    def check_collision(self, bullet):
        distance = self.position.distance_to(bullet.position)
        return distance < (self.radius * self.scale + bullet.size)
        
    def check_projectile_collisions_with_player(self, player):
        hits = []
        for i, projectile in enumerate(self.projectiles):
            if projectile.check_collision_with_player(player):
                hits.append(i)
        
        # Remove hit projectiles
        for i in reversed(hits):
            self.projectiles.pop(i)
            
        return len(hits) > 0
        
    def check_projectile_collisions_with_cover(self, cover_system):
        hits = []
        for i, projectile in enumerate(self.projectiles):
            if cover_system.check_projectile_collision(projectile.position, projectile.size):
                hits.append(i)
        
        # Remove hit projectiles
        for i in reversed(hits):
            self.projectiles.pop(i)

class Player:
    def __init__(self):
        self.position = Vector3(0, 0, 30)
        self.angle = 0  
        self.lying = False
        self.crouching = False
        self.hiding_behind_cover = False
        self.current_cover = None
        self.grid_size = 60
        self.crouch_height = 15  # Reduced height when crouching
        self.normal_height = 30
        self.detection_radius = 15  # Player detection radius
        
        # Humanoid hitbox components
        self.head_radius = 4
        self.torso_width = 6
        self.torso_height = 12
        self.limb_radius = 2
        
        # Movement state for diagonal movement
        self.movement_keys = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False
        }
        self.move_speed = 4  # Movement speed per frame
        self.gun_angle = 0  # Independent gun aiming angle
        
        # Animation system
        self.animation_time = 0
        self.walking = False
        self.walk_cycle_speed = 0.2
        self.arm_swing_amplitude = 15  # degrees
        self.leg_swing_amplitude = 20  # degrees
        
        # Smooth rotation system
        self.target_angle = 0  # Target angle for smooth rotation
        self.rotation_speed = 8.0  # Degrees per frame for smooth rotation
        self.rotation_threshold = 1.0  # Minimum angle difference to trigger rotation 
    
    def set_movement_key(self, direction, pressed):
        """Set movement key state for diagonal movement"""
        if direction in self.movement_keys:
            self.movement_keys[direction] = pressed
    
    def check_collision_at_position(self, new_position, cover_system=None, enemies=None):
        """Check if the player would collide with any objects at the given position"""
        player_radius = 20  # Player collision radius
        
        # Check collision with cover objects
        if cover_system:
            for cover in cover_system.covers:
                if not cover.destroyed:
                    # Check collision with cover using expanded bounds
                    half_w = cover.width / 2 + player_radius
                    half_h = cover.height / 2 + player_radius
                    half_d = cover.depth / 2 + player_radius
                    
                    if (abs(new_position.x - cover.position.x) < half_w and
                        abs(new_position.y - cover.position.y) < half_h and
                        abs(new_position.z - cover.position.z) < half_d):
                        return True
        
        # Check collision with enemies (maintain minimum distance)
        if enemies:
            for enemy in enemies:
                distance = new_position.distance_to(enemy.position)
                if distance < (player_radius + enemy.radius * enemy.scale):
                    return True
        
        return False
    
    def update_movement(self, cover_system=None, enemies=None):
        """Update player position based on current movement keys relative to gun direction"""
        if self.lying:
            return
        
        # Calculate movement vector relative to gun direction
        move_forward = 0
        move_strafe = 0
        
        if self.movement_keys['forward']:
            move_forward += self.move_speed
        if self.movement_keys['backward']:
            move_forward -= self.move_speed
        if self.movement_keys['left']:
            move_strafe -= self.move_speed
        if self.movement_keys['right']:
            move_strafe += self.move_speed
        
        # Update walking state for animation
        self.walking = (move_forward != 0 or move_strafe != 0)
        
        # Normalize diagonal movement to prevent faster diagonal speed
        if move_forward != 0 and move_strafe != 0:
            diagonal_factor = 0.707  # 1/sqrt(2)
            move_forward *= diagonal_factor
            move_strafe *= diagonal_factor
        
        # Convert movement to world coordinates based on gun angle
        gun_angle_rad = math.radians(self.gun_angle)
        
        # Forward/backward movement in gun direction
        forward_x = math.sin(gun_angle_rad) * move_forward
        forward_y = math.cos(gun_angle_rad) * move_forward
        
        # Strafe movement perpendicular to gun direction
        strafe_x = math.cos(gun_angle_rad) * move_strafe
        strafe_y = -math.sin(gun_angle_rad) * move_strafe
        
        # Combine movements
        move_x = forward_x + strafe_x
        move_y = forward_y + strafe_y
        
        # Calculate new position
        new_x = self.position.x + move_x
        new_y = self.position.y + move_y
        new_position = Vector3(new_x, new_y, self.position.z)
        
        # Check boundary limits
        if abs(new_x) >= 540 or abs(new_y) >= 540:
            return  # Don't move if hitting world boundaries
        
        # Check collision with scene objects
        if not self.check_collision_at_position(new_position, cover_system, enemies):
            # Only update position if no collision detected
            self.position.x = new_x
            self.position.y = new_y
        
        # Update animation
        self.update_animation()
    
    def move_forward(self):
        """Legacy method for backward compatibility"""
        self.set_movement_key('forward', True)
    
    def move_backward(self):
        """Legacy method for backward compatibility"""
        self.set_movement_key('backward', True)
    
    def rotate_left(self):
        """Rotate player and gun together left with smooth motion"""
        if not self.lying:
            self.target_angle += 20
            if self.target_angle >= 360:
                self.target_angle -= 360
    
    def rotate_right(self):
        """Rotate player and gun together right with smooth motion"""
        if not self.lying:
            self.target_angle -= 20
            if self.target_angle < 0:
                self.target_angle += 360
    
    def aim_gun_left(self):
        """Fine-tune aiming left with smooth motion"""
        if not self.lying:
            self.target_angle -= 5  # Reversed: now rotates clockwise
            if self.target_angle < 0:
                self.target_angle += 360
    
    def aim_gun_right(self):
        """Fine-tune aiming right with smooth motion"""
        if not self.lying:
            self.target_angle += 5  # Reversed: now rotates counterclockwise
            if self.target_angle >= 360:
                self.target_angle -= 360
    
    def set_gun_angle(self, angle):
        """Set target angle directly for 360-degree aiming"""
        self.target_angle = angle % 360
    
    def get_gun_direction(self):
        """Get gun direction based on current unified angle"""
        angle_rad = math.radians(self.angle)
        return Vector3(math.sin(angle_rad), math.cos(angle_rad), 0)
    
    def update_animation(self):
        """Update animation state and smooth rotation"""
        # Update walking animation
        if self.walking:
            self.animation_time += self.walk_cycle_speed
        else:
            # Gradually return to neutral position when not walking
            self.animation_time *= 0.9
            if abs(self.animation_time) < 0.01:
                self.animation_time = 0
        
        # Update smooth rotation
        self.update_smooth_rotation()
    
    def update_smooth_rotation(self):
        """Smoothly interpolate between current and target angles"""
        if not self.lying:
            # Calculate the shortest angular distance
            angle_diff = self.target_angle - self.angle
            
            # Handle angle wrapping (shortest path)
            if angle_diff > 180:
                angle_diff -= 360
            elif angle_diff < -180:
                angle_diff += 360
            
            # Apply smooth rotation if difference is significant
            if abs(angle_diff) > self.rotation_threshold:
                # Interpolate towards target angle
                rotation_step = min(abs(angle_diff), self.rotation_speed)
                if angle_diff > 0:
                    self.angle += rotation_step
                else:
                    self.angle -= rotation_step
                
                # Keep angle in 0-360 range
                self.angle = self.angle % 360
                
                # Sync gun angle with player angle for unified rotation
                self.gun_angle = self.angle
            else:
                # Snap to target if very close
                self.angle = self.target_angle
                self.gun_angle = self.angle
    
    def get_gun_tip_position(self):
        """Get gun tip position for bullet spawning"""
        direction = self.get_gun_direction()
        return self.position + (direction * 30)  # Adjusted for forward gun positioning 
    
    def lie_down(self):
        self.lying = True
        self.crouching = False
    
    def crouch(self):
        """Toggle crouching state"""
        if not self.lying:
            self.crouching = not self.crouching
            if self.crouching:
                self.position.z = self.crouch_height
                print("Player crouching - harder to detect!")
            else:
                self.position.z = self.normal_height
                print("Player standing up")
    
    def check_cover_status(self, cover_system, enemies):
        """Check if player is behind cover relative to enemies"""
        self.hiding_behind_cover = False
        self.current_cover = None
        
        for enemy in enemies:
            cover = cover_system.get_cover_for_player(self.position, enemy.position)
            if cover:
                self.hiding_behind_cover = True
                self.current_cover = cover
                break
    
    def get_detection_modifier(self):
        """Get detection difficulty modifier based on player state"""
        modifier = 1.0
        
        if self.crouching:
            modifier *= 0.7  # 30% harder to detect when crouching
        
        if self.lying:
            modifier *= 0.5  # 50% harder to detect when lying
            
        if self.hiding_behind_cover:
            modifier *= 0.3  # 70% harder to detect behind cover
            
        return modifier
    
    def is_hidden_from_enemy(self, enemy_position, cover_system):
        """Check if player is hidden from a specific enemy"""
        # Check if there's cover between player and enemy
        for cover in cover_system.covers:
            if cover.provides_cover_for(self.position, enemy_position):
                return True
        return False
    
    def get_head_position(self):
        """Get the position of the player's head"""
        height = self.crouch_height if self.crouching else self.normal_height
        return Vector3(self.position.x, self.position.y, self.position.z + height - 2)
    
    def get_torso_position(self):
        """Get the position of the player's torso center"""
        height = self.crouch_height if self.crouching else self.normal_height
        return Vector3(self.position.x, self.position.y, self.position.z + height/2)
    
    def get_hitbox_components(self):
        """Get all hitbox components for collision detection"""
        components = []
        
        # Head hitbox
        head_pos = self.get_head_position()
        components.append({
            'position': head_pos,
            'radius': self.head_radius,
            'type': 'head'
        })
        
        # Torso hitbox
        torso_pos = self.get_torso_position()
        components.append({
            'position': torso_pos,
            'width': self.torso_width,
            'height': self.torso_height,
            'type': 'torso'
        })
        
        return components
    
    def check_collision_with_projectile(self, projectile_pos, projectile_radius=3):
        """Check if a projectile collides with any part of the humanoid player"""
        components = self.get_hitbox_components()
        
        for component in components:
            if component['type'] == 'head':
                # Sphere collision for head
                distance = component['position'].distance_to(projectile_pos)
                if distance < (component['radius'] + projectile_radius):
                    return True
            elif component['type'] == 'torso':
                # Box collision for torso
                pos = component['position']
                half_w = component['width'] / 2 + projectile_radius
                half_h = component['height'] / 2 + projectile_radius
                
                if (abs(projectile_pos.x - pos.x) < half_w and
                    abs(projectile_pos.y - pos.y) < half_w and
                    abs(projectile_pos.z - pos.z) < half_h):
                    return True
        
        return False
    
    def reset(self):
        self.position = Vector3(0, 0, 30)
        self.angle = 0
        self.lying = False
        self.crouching = False
        self.hiding_behind_cover = False
        self.current_cover = None
        self.gun_angle = 0
        # Reset animation state
        self.animation_time = 0
        self.walking = False
        # Reset smooth rotation state
        self.target_angle = 0
        # Reset movement keys
        for key in self.movement_keys:
            self.movement_keys[key] = False
    
    def draw(self):
        glPushMatrix()
        
        if self.lying:
            glTranslatef(self.position.x, self.position.y, 15)
            glRotatef(90, 1, 0, 0) 
        else:
            glTranslatef(self.position.x, self.position.y, self.position.z)
            glRotatef(self.angle, 0, 0, 1)
        
        # Draw humanoid body structure
        self.draw_humanoid_body()
        
        glPopMatrix()
    
    def draw_humanoid_body(self):
        """Draw humanoid player with head, torso, arms, and legs"""
        
        # Head
        glPushMatrix()
        glTranslatef(0, 0, 20)
        glColor3f(0.9, 0.7, 0.6)  # Skin color
        glutSolidSphere(8, 12, 12)
        glPopMatrix()
        
        # Torso
        glPushMatrix()
        glTranslatef(0, 0, 5)
        glColor3f(0.2, 0.4, 0.8)  # Blue shirt
        glScalef(1.0, 0.6, 1.8)
        glutSolidCube(12)
        glPopMatrix()
        
        # Calculate animation angles
        arm_swing = math.sin(self.animation_time) * self.arm_swing_amplitude if self.walking else 0
        leg_swing = math.sin(self.animation_time) * self.leg_swing_amplitude if self.walking else 0
        
        # Arms with animation
        # Left arm (swings opposite to right leg)
        glPushMatrix()
        glTranslatef(-10, 0, 8)
        glRotatef(-arm_swing, 1, 0, 0)  # Swing forward/backward
        glColor3f(0.9, 0.7, 0.6)  # Skin color
        glScalef(0.6, 0.6, 1.2)
        glutSolidCube(8)
        glPopMatrix()
        
        # Right arm (swings opposite to left leg)
        glPushMatrix()
        glTranslatef(10, 0, 8)
        glRotatef(arm_swing, 1, 0, 0)  # Swing forward/backward
        glColor3f(0.9, 0.7, 0.6)  # Skin color
        glScalef(0.6, 0.6, 1.2)
        glutSolidCube(8)
        glPopMatrix()
        
        # Legs with animation
        # Left leg
        glPushMatrix()
        glTranslatef(-4, 0, -8)
        glRotatef(leg_swing, 1, 0, 0)  # Swing forward/backward
        glColor3f(0.1, 0.1, 0.4)  # Dark blue pants
        glScalef(0.7, 0.7, 1.5)
        glutSolidCube(8)
        glPopMatrix()
        
        # Right leg
        glPushMatrix()
        glTranslatef(4, 0, -8)
        glRotatef(-leg_swing, 1, 0, 0)  # Swing forward/backward
        glColor3f(0.1, 0.1, 0.4)  # Dark blue pants
        glScalef(0.7, 0.7, 1.5)
        glutSolidCube(8)
        glPopMatrix()
        
        # Feet
        # Left foot
        glPushMatrix()
        glTranslatef(-4, 3, -15)
        glColor3f(0.2, 0.1, 0.0)  # Brown shoes
        glScalef(0.8, 1.2, 0.4)
        glutSolidCube(6)
        glPopMatrix()
        
        # Right foot
        glPushMatrix()
        glTranslatef(4, 3, -15)
        glColor3f(0.2, 0.1, 0.0)  # Brown shoes
        glScalef(0.8, 1.2, 0.4)
        glutSolidCube(6)
        glPopMatrix()
        
        # Draw visible gun
        self.draw_gun()
    
    def draw_gun(self):
        """Draw visible gun attached to the player with unified rotation"""
        
        # Gun now rotates with player body - no additional rotation needed
        glPushMatrix()
        
        # Gun barrel
        glPushMatrix()
        glTranslatef(0, 20, 8)  # Position gun further forward for better visibility
        glRotatef(90, 1, 0, 0)  # Rotate to point forward
        glColor3f(0.2, 0.2, 0.2)  # Dark gray metal
        gluCylinder(gluNewQuadric(), 2, 2, 25, 12, 12)
        glPopMatrix()
        
        # Gun body/receiver
        glPushMatrix()
        glTranslatef(0, 13, 8)  # Adjusted to maintain proper attachment
        glColor3f(0.3, 0.3, 0.3)  # Lighter gray
        glScalef(1.2, 0.8, 0.6)
        glutSolidCube(8)
        glPopMatrix()
        
        # Gun grip
        glPushMatrix()
        glTranslatef(0, 10, 3)  # Adjusted to maintain proper attachment
        glColor3f(0.1, 0.1, 0.1)  # Black grip
        glScalef(0.8, 0.6, 1.0)
        glutSolidCube(6)
        glPopMatrix()
        
        # Gun sight
        glPushMatrix()
        glTranslatef(0, 23, 10)  # Adjusted to stay at barrel tip for aiming reference
        glColor3f(0.8, 0.8, 0.1)  # Yellow sight
        glutSolidSphere(1, 8, 8)
        glPopMatrix()
        
        glPopMatrix()  # End gun rotation

class Camera:
    def __init__(self):
        self.position = Vector3(0, 600, 600)
        self.angle = 0
        self.height = 600
        self.first_person = False
        self.fov = 120
    
    def rotate_left(self):
  
        self.angle -= 10
        self.update_position()
    
    def rotate_right(self):
  
        self.angle += 10
        self.update_position()
    
    def move_up(self):
  
        self.height += 30
        self.update_position()
    
    def move_down(self):
  
        self.height -= 30
        if self.height < 150:
            self.height = 150
        self.update_position()
    
    def update_position(self):
  
        if not self.first_person:
            radius = 800
            camera_x = radius * math.sin(math.radians(self.angle))
            camera_y = radius * math.cos(math.radians(self.angle))
            self.position = Vector3(camera_x, camera_y, self.height)
    
    def toggle_first_person(self):
  
        self.first_person = not self.first_person
    
    def setup(self, player, screen_shake_offset=None):
  
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, 1.25, 0.1, 2000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # Apply screen shake if provided
        shake_x = screen_shake_offset.x if screen_shake_offset else 0
        shake_y = screen_shake_offset.y if screen_shake_offset else 0
        shake_z = screen_shake_offset.z if screen_shake_offset else 0

        if self.first_person:
            eye_height = 40 
            eye_distance_back = 15  

            gun_direction = player.get_gun_direction()
            
            eye_pos = Vector3(
                player.position.x - gun_direction.x * eye_distance_back + shake_x,
                player.position.y - gun_direction.y * eye_distance_back + shake_y,
                player.position.z + eye_height + shake_z
            )
            
            look_distance = 300
            look_at = Vector3(
                eye_pos.x + gun_direction.x * look_distance,
                eye_pos.y + gun_direction.y * look_distance,
                eye_pos.z - 10  
            )
            
            gluLookAt(eye_pos.x, eye_pos.y, eye_pos.z,
                      look_at.x, look_at.y, look_at.z,
                      0, 0, 1)
        else:
            gluLookAt(self.position.x + shake_x, self.position.y + shake_y, self.position.z + shake_z,
                        0, 0, 60, 0, 0, 1)

class Skybox:
    def __init__(self):
        self.sun_rotation = 0
        self.moon_rotation = 0
        self.star_rotation = 0
        self.time = 0
        
    def update(self):
        self.time += 0.02
        self.sun_rotation += 0.5
        self.moon_rotation += 0.3
        self.star_rotation += 0.1
        
        if self.sun_rotation >= 360:
            self.sun_rotation -= 360
        if self.moon_rotation >= 360:
            self.moon_rotation -= 360
        if self.star_rotation >= 360:
            self.star_rotation -= 360
    
    def draw(self):
        glPushMatrix()
        
        # Draw distant stars as small spheres
        for i in range(20):
            angle = i * 18  # 360/20 = 18 degrees apart
            radius = 1200
            
            glPushMatrix()
            glRotatef(self.star_rotation + angle, 0, 0, 1)
            glTranslatef(radius, 0, 400 + 100 * math.sin(self.time + i))
            glColor3f(1.0, 1.0, 0.8)
            glutSolidSphere(8, 6, 6)
            glPopMatrix()
        
        # Draw animated sun
        glPushMatrix()
        glRotatef(self.sun_rotation, 0, 0, 1)
        glTranslatef(800, 0, 600)
        glColor3f(1.0, 0.8, 0.0)
        glutSolidSphere(60, 12, 12)
        
        # Sun rays using cylinders
        for i in range(8):
            glPushMatrix()
            glRotatef(i * 45, 0, 0, 1)
            glTranslatef(80, 0, 0)
            glRotatef(90, 0, 1, 0)
            glColor3f(1.0, 0.9, 0.2)
            gluCylinder(gluNewQuadric(), 3, 1, 30, 6, 6)
            glPopMatrix()
        glPopMatrix()
        
        # Draw animated moon
        glPushMatrix()
        glRotatef(self.moon_rotation, 0, 0, 1)
        glTranslatef(-700, 0, 500)
        glColor3f(0.8, 0.8, 0.9)
        glutSolidSphere(40, 10, 10)
        
        # Moon craters
        glPushMatrix()
        glTranslatef(15, 15, 20)
        glColor3f(0.6, 0.6, 0.7)
        glutSolidSphere(8, 6, 6)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(-10, 20, 25)
        glColor3f(0.6, 0.6, 0.7)
        glutSolidSphere(5, 6, 6)
        glPopMatrix()
        glPopMatrix()
        
        # Draw floating celestial rings
        for i in range(3):
            glPushMatrix()
            glRotatef(self.time * 20 + i * 120, 0, 0, 1)
            glTranslatef(900 + i * 100, 0, 700 + i * 50)
            glRotatef(90, 1, 0, 0)
            glColor3f(0.5 + i * 0.2, 0.3, 0.8 - i * 0.2)
            
            # Create ring using cylinder with hollow center
            gluCylinder(gluNewQuadric(), 30 + i * 10, 35 + i * 10, 5, 16, 1)
            glPopMatrix()
        
        glPopMatrix()

class Bomb:
    def __init__(self, position):
        self.position = Vector3(position.x, position.y, position.z)
        self.radius = 20
        self.exploded = False
        self.explosion_timer = 0
        self.explosion_duration = 60  # frames
        self.blink_timer = 0
        self.blink_speed = 10
        self.warning_phase = False
        self.warning_timer = 0
        self.warning_duration = 180  # 3 seconds at 60fps
        self.hit_count = 0
        self.max_hits = 3
        self.destroyed = False
        # Color transition system
        self.base_color = (0.1, 1.0, 0.1)  # Bright green
        self.current_color = self.base_color
        # Flash effect for immediate visual feedback
        self.flash_timer = 0
        self.flash_duration = 10  # frames
        self.is_flashing = False
        
    def update(self):
        """Update bomb state and timers"""
        if not self.exploded:
            self.blink_timer += 1
            self.warning_timer += 1
            
            # Handle flash effect
            if self.is_flashing:
                self.flash_timer += 1
                if self.flash_timer >= self.flash_duration:
                    self.is_flashing = False
                    self.flash_timer = 0
            
            # Enter warning phase before explosion
            if self.warning_timer > self.warning_duration:
                self.warning_phase = True
                self.blink_speed = 5  # Faster blinking
        else:
            self.explosion_timer += 1
            
    def explode(self):
        """Trigger bomb explosion"""
        if not self.exploded:
            self.exploded = True
            self.explosion_timer = 0
            print("BOMB EXPLODED!")
            
    def is_explosion_finished(self):
        """Check if explosion animation is complete"""
        return self.exploded and self.explosion_timer >= self.explosion_duration
        
    def check_collision(self, player):
        """Check if player collides with bomb"""
        if self.exploded:
            return False
            
        # Use humanoid collision detection if available
        if hasattr(player, 'get_hitbox_components'):
            components = player.get_hitbox_components()
            for component in components:
                distance = self.position.distance_to(component['position'])
                if distance < (self.radius + component.get('radius', 10)):
                    return True
        else:
            # Fallback to simple collision
            distance = self.position.distance_to(player.position)
            return distance < (self.radius + 25)
            
        return False
    
    def update_color_based_on_hits(self):
        """Update bomb color based on hit count with enhanced visibility"""
        if self.hit_count == 0:
            # Bright green (no hits)
            self.current_color = (0.1, 1.0, 0.1)
        elif self.hit_count == 1:
            # Bright yellow (1 hit) - very noticeable change
            self.current_color = (1.0, 1.0, 0.0)
        elif self.hit_count == 2:
            # Bright orange (2 hits) - warning color
            self.current_color = (1.0, 0.5, 0.0)
        else:
            # Bright red (3+ hits) - danger color
            self.current_color = (1.0, 0.0, 0.0)
    
    def check_bullet_collision(self, bullet_pos, bullet_radius=3):
        """Check if bullet collides with bomb and handle hit counting"""
        if self.exploded or self.destroyed:
            return False
            
        distance = self.position.distance_to(bullet_pos)
        if distance < (self.radius + bullet_radius):
            self.hit_count += 1
            self.update_color_based_on_hits()  # Update color on hit
            # Trigger flash effect for immediate visual feedback
            self.is_flashing = True
            self.flash_timer = 0
            print(f"Bomb hit! ({self.hit_count}/{self.max_hits})")
            
            if self.hit_count >= self.max_hits:
                self.destroyed = True
                print("Bomb destroyed by bullets!")
                return True
            return True
        return False
        
    def draw(self):
        """Draw bomb with blinking effect and explosion animation"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        if not self.exploded:
            # Blinking bomb effect with color transition
            blink_on = (self.blink_timer // self.blink_speed) % 2 == 0
            
            if blink_on:
                if self.warning_phase:
                    glColor3f(1.0, 0.0, 0.0)  # Red warning (overrides hit color)
                else:
                    # Use hit-based color
                    glColor3f(*self.current_color)
            else:
                if self.warning_phase:
                    glColor3f(1.0, 0.5, 0.0)  # Orange warning
                else:
                    # Darker version of hit-based color for blink effect
                    r, g, b = self.current_color
                    glColor3f(r * 0.4, g * 0.4, b * 0.4)
            
            # Draw the main bomb sphere
            glutSolidSphere(self.radius, 16, 16)
            
            # Draw the fuse
            glPushMatrix()
            glTranslatef(0, 0, self.radius)
            glColor3f(0.8, 0.4, 0.0)  # Brown fuse
            glScalef(2, 2, 8)
            glutSolidCube(2)
            glPopMatrix()
            
        else:
            # Explosion animation
            explosion_progress = self.explosion_timer / self.explosion_duration
            explosion_size = self.radius * (1 + explosion_progress * 3)
            
            # Multiple explosion layers for effect
            for i in range(3):
                glPushMatrix()
                layer_size = explosion_size * (1 - i * 0.2)
                alpha = 1.0 - explosion_progress
                
                if i == 0:
                    glColor4f(1.0, 1.0, 0.0, alpha)  # Yellow core
                elif i == 1:
                    glColor4f(1.0, 0.5, 0.0, alpha * 0.7)  # Orange middle
                else:
                    glColor4f(1.0, 0.0, 0.0, alpha * 0.5)  # Red outer
                    
                glutSolidSphere(layer_size, 16, 16)
                glPopMatrix()
                
        glPopMatrix()

class BombSystem:
    def __init__(self):
        self.bombs = []
        self.spawn_timer = 0
        self.spawn_interval = 600  # 10 seconds at 60fps
        self.max_bombs = 5
        
    def initialize_bombs(self):
        """Initialize bombs at random positions"""
        self.bombs.clear()
        
        # Spawn initial bombs
        for _ in range(3):
            self.spawn_bomb()
            
    def spawn_bomb(self):
        """Spawn a new bomb at random position"""
        if len(self.bombs) >= self.max_bombs:
            return
            
        # Random position on grid
        grid_size = 80
        grid_x = random.randint(-6, 6)
        grid_y = random.randint(-6, 6)
        
        x = grid_x * grid_size
        y = grid_y * grid_size
        z = 20
        
        bomb = Bomb(Vector3(x, y, z))
        self.bombs.append(bomb)
        print(f"Bomb spawned at ({x}, {y}, {z})")
        
    def update(self):
        """Update all bombs and handle spawning"""
        # Update existing bombs
        for bomb in self.bombs[:]:
            bomb.update()
            
            # Remove finished explosions
            if bomb.is_explosion_finished():
                self.bombs.remove(bomb)
                
        # Spawn new bombs periodically
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_bomb()
            self.spawn_timer = 0
            
    def check_bullet_collisions(self, bullets):
        """Check if any bullets hit bombs and handle destruction/respawn"""
        hit_bullets = []
        destroyed_bombs = []
        
        for bullet in bullets:
            for bomb in self.bombs[:]:
                if bomb.check_bullet_collision(bullet.position):
                    hit_bullets.append(bullet)
                    
                    if bomb.destroyed:
                        # Create explosion effect
                        destroyed_bombs.append(bomb)
                        self.bombs.remove(bomb)
                        
                        # Spawn new bomb at different location
                        self.spawn_bomb()
                        print("New bomb spawned after destruction!")
                    break
        
        return hit_bullets, destroyed_bombs
    
    def check_collisions(self, player):
        """Check if player collides with any bomb"""
        exploded_bombs = []
        for bomb in self.bombs:
            if bomb.check_collision(player):
                bomb.explode()
                exploded_bombs.append(bomb)
        return exploded_bombs
        
    def draw(self):
        """Draw all bombs"""
        for bomb in self.bombs:
            bomb.draw()
            
    def clear_all(self):
        """Clear all bombs (for game reset)"""
        self.bombs.clear()

class PowerUp:
    def __init__(self, position, power_type):
        self.position = Vector3(position.x, position.y, position.z)
        self.power_type = power_type  # 'health', 'speed', 'damage', 'shield', 'bullet'
        self.rotation = 0
        self.pulse_time = 0
        self.collected = False
        self.radius = 20
        
        # Power-up specific properties
        self.colors = {
            'health': (0.0, 1.0, 0.0),    # Green
            'speed': (0.0, 0.0, 1.0),     # Blue
            'damage': (1.0, 0.0, 0.0),    # Red
            'shield': (1.0, 1.0, 0.0),    # Yellow
            'bullet': (1.0, 0.5, 0.0)     # Orange
        }
        
        self.symbols = {
            'health': '+',
            'speed': '>',
            'damage': '*',
            'shield': 'S',
            'bullet': 'B'
        }
    
    def update(self):
        if not self.collected:
            self.rotation += 2
            self.pulse_time += 0.1
            
            if self.rotation >= 360:
                self.rotation -= 360
    
    def draw(self):
        if self.collected:
            return
            
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Floating animation
        float_offset = 10 * math.sin(self.pulse_time)
        glTranslatef(0, 0, float_offset)
        
        # Rotation animation
        glRotatef(self.rotation, 0, 0, 1)
        glRotatef(self.pulse_time * 30, 1, 0, 0)
        
        # Pulsating scale
        scale = 1.0 + 0.3 * math.sin(self.pulse_time * 2)
        glScalef(scale, scale, scale)
        
        # Draw heart shape
        color = self.colors[self.power_type]
        glColor3f(color[0], color[1], color[2])
        
        # Heart shape using spheres and mathematical positioning
        # Main body of heart (bottom point)
        glPushMatrix()
        glTranslatef(0, -8, 0)
        glScalef(0.8, 1.2, 0.8)
        glutSolidSphere(8, 12, 12)
        glPopMatrix()
        
        # Left lobe of heart
        glPushMatrix()
        glTranslatef(-6, 2, 0)
        glutSolidSphere(7, 12, 12)
        glPopMatrix()
        
        # Right lobe of heart
        glPushMatrix()
        glTranslatef(6, 2, 0)
        glutSolidSphere(7, 12, 12)
        glPopMatrix()
        
        # Center connection
        glPushMatrix()
        glTranslatef(0, 0, 0)
        glScalef(1.2, 0.8, 0.8)
        glutSolidSphere(6, 12, 12)
        glPopMatrix()
        
        # Inner glowing core (smaller heart)
        glColor3f(1.0, 1.0, 1.0)  # White core
        
        # Core main body
        glPushMatrix()
        glTranslatef(0, -6, 0)
        glScalef(0.6, 0.8, 0.6)
        glutSolidSphere(5, 8, 8)
        glPopMatrix()
        
        # Core left lobe
        glPushMatrix()
        glTranslatef(-4, 1, 0)
        glutSolidSphere(4, 8, 8)
        glPopMatrix()
        
        # Core right lobe
        glPushMatrix()
        glTranslatef(4, 1, 0)
        glutSolidSphere(4, 8, 8)
        glPopMatrix()
        
        # Sparkle effect around heart
        glColor3f(color[0] * 0.8, color[1] * 0.8, color[2] * 0.8)
        for i in range(8):
            angle = (i * 45 + self.rotation * 2) * math.pi / 180
            x = 15 * math.cos(angle)
            y = 15 * math.sin(angle)
            glPushMatrix()
            glTranslatef(x, y, 0)
            glutSolidSphere(1.5, 6, 6)
            glPopMatrix()
        glPopMatrix()
    
    def check_collision(self, player):
        if self.collected:
            return False
        
        # Use humanoid collision detection if available
        if hasattr(player, 'get_hitbox_components'):
            components = player.get_hitbox_components()
            for component in components:
                if component['type'] == 'torso':
                    # Check collision with torso (main body)
                    pos = component['position']
                    distance = self.position.distance_to(pos)
                    return distance < (self.radius + 15)  # Adjusted for torso
        else:
            # Fallback to simple collision
            distance = self.position.distance_to(player.position)
            return distance < (self.radius + 25)  # Player radius
        
        return False
    
    def collect(self):
        self.collected = True
        return self.power_type

class PowerUpSystem:
    def __init__(self):
        self.power_ups = []
        self.spawn_timer = 0
        self.spawn_interval = 300  # Spawn every 5 seconds at 60 FPS
        
    def update(self):
        self.spawn_timer += 1
        
        # Spawn new power-ups periodically
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_power_up()
            self.spawn_timer = 0
        
        # Update existing power-ups
        for power_up in self.power_ups:
            power_up.update()
        
        # Remove collected power-ups
        self.power_ups = [p for p in self.power_ups if not p.collected]
    
    def spawn_power_up(self):
        # Random position on grid
        grid_size = 60
        grid_x = random.randint(-8, 8)
        grid_y = random.randint(-8, 8)
        
        x = grid_x * grid_size
        y = grid_y * grid_size
        z = 40
        
        power_types = ['health', 'speed', 'damage', 'shield', 'bullet']
        power_type = random.choice(power_types)
        
        power_up = PowerUp(Vector3(x, y, z), power_type)
        self.power_ups.append(power_up)
    
    def draw(self):
        for power_up in self.power_ups:
            power_up.draw()
    
    def check_collisions(self, player):
        collected_powers = []
        for power_up in self.power_ups:
            if power_up.check_collision(player):
                power_type = power_up.collect()
                collected_powers.append(power_type)
        return collected_powers

class Avatar:
    def __init__(self, position):
        self.position = Vector3(position.x, position.y, position.z)
        self.radius = 25
        
        # Face orientation properties
        self.current_face_angle = 0.0  # Current face direction (0 = forward, 180 = backward)
        self.target_face_angle = 0.0   # Target face direction for smooth rotation
        self.is_rotating = False
        
        # Animation properties
        self.rotation_speed = 5.0      # Degrees per frame
        self.animation_timer = 0
        self.rotation_progress = 0.0   # 0.0 to 1.0 for interpolation
        
        # Visual consistency properties
        self.head_tilt = 0.0          # Head tilt during rotation
        self.eye_blink_timer = 0
        self.expression_state = 'neutral'  # 'neutral', 'surprised', 'focused'
        
        # Input handling
        self.rotation_triggered = False
        
    def trigger_face_rotation(self):
        """Trigger a 180-degree face rotation"""
        if not self.is_rotating:
            self.target_face_angle = (self.current_face_angle + 180) % 360
            self.is_rotating = True
            self.rotation_progress = 0.0
            self.animation_timer = 0
            self.expression_state = 'surprised'
            print(f"Avatar face rotation triggered: {self.current_face_angle}° -> {self.target_face_angle}°")
    
    def update(self):
        """Update avatar animation and rotation state"""
        if self.is_rotating:
            # Smooth rotation animation with easing
            self.animation_timer += 1
            max_frames = 60  # 1 second at 60fps
            
            if self.animation_timer <= max_frames:
                # Ease-in-out interpolation
                t = self.animation_timer / max_frames
                self.rotation_progress = self.ease_in_out(t)
                
                # Calculate current angle with smooth interpolation
                angle_diff = self.target_face_angle - self.current_face_angle
                if angle_diff > 180:
                    angle_diff -= 360
                elif angle_diff < -180:
                    angle_diff += 360
                    
                self.current_face_angle = (self.current_face_angle + 
                                         angle_diff * self.rotation_progress) % 360
                
                # Add head tilt for natural movement
                self.head_tilt = math.sin(self.rotation_progress * math.pi) * 15
            else:
                # Complete rotation
                self.current_face_angle = self.target_face_angle
                self.is_rotating = False
                self.rotation_progress = 1.0
                self.head_tilt = 0.0
                self.expression_state = 'neutral'
                print(f"Avatar face rotation completed at {self.current_face_angle}°")
        
        # Eye blink animation
        self.eye_blink_timer += 1
        if self.eye_blink_timer > 180:  # Blink every 3 seconds
            self.eye_blink_timer = 0
    
    def ease_in_out(self, t):
        """Smooth easing function for natural animation"""
        return t * t * (3.0 - 2.0 * t)
    
    def draw(self):
        """Draw avatar with dynamic face rotation"""
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Apply head tilt for natural movement
        glRotatef(self.head_tilt, 1, 0, 0)
        
        # Draw body (remains stationary)
        self.draw_body()
        
        # Draw head with face rotation
        glPushMatrix()
        glTranslatef(0, 0, 40)  # Head position
        glRotatef(self.current_face_angle, 0, 0, 1)  # Face rotation
        self.draw_head()
        glPopMatrix()
        
        glPopMatrix()
    
    def draw_body(self):
        """Draw avatar body"""
        # Torso
        glColor3f(0.2, 0.4, 0.8)  # Blue shirt
        glPushMatrix()
        glScalef(15, 8, 30)
        glutSolidCube(1)
        glPopMatrix()
        
        # Arms
        glColor3f(0.8, 0.6, 0.4)  # Skin tone
        for x_offset in [-12, 12]:
            glPushMatrix()
            glTranslatef(x_offset, 0, 10)
            glScalef(4, 4, 20)
            glutSolidCube(1)
            glPopMatrix()
    
    def draw_head(self):
        """Draw avatar head with facial features"""
        # Head
        glColor3f(0.8, 0.6, 0.4)  # Skin tone
        glutSolidSphere(12, 16, 16)
        
        # Eyes
        eye_open = self.eye_blink_timer > 5  # Blink effect
        eye_size = 2 if eye_open else 0.5
        
        glColor3f(1.0, 1.0, 1.0)  # White eyes
        for x_offset in [-4, 4]:
            glPushMatrix()
            glTranslatef(x_offset, 8, 2)
            glutSolidSphere(eye_size, 8, 8)
            glPopMatrix()
        
        if eye_open:
            # Pupils
            glColor3f(0.0, 0.0, 0.0)  # Black pupils
            for x_offset in [-4, 4]:
                glPushMatrix()
                glTranslatef(x_offset, 9, 2)
                glutSolidSphere(1, 6, 6)
                glPopMatrix()
        
        # Nose
        glColor3f(0.7, 0.5, 0.3)  # Slightly darker skin
        glPushMatrix()
        glTranslatef(0, 6, 0)
        glScalef(1, 2, 3)
        glutSolidCube(1)
        glPopMatrix()
        
        # Mouth (changes with expression)
        glColor3f(0.6, 0.2, 0.2)  # Red mouth
        glPushMatrix()
        glTranslatef(0, 4, -2)
        if self.expression_state == 'surprised':
            glutSolidSphere(2, 8, 8)  # Open mouth
        else:
            glScalef(4, 1, 1)
            glutSolidCube(1)  # Normal mouth
        glPopMatrix()

class Particle:
    def __init__(self, position, velocity, color, size, lifetime):
        self.position = Vector3(position.x, position.y, position.z)
        self.velocity = Vector3(velocity.x, velocity.y, velocity.z)
        self.color = color  # (r, g, b, alpha)
        self.size = size
        self.lifetime = lifetime
        self.age = 0
        self.gravity = -0.5
        self.fade_rate = 1.0 / lifetime
        
    def update(self):
        # Update position
        self.position = self.position + self.velocity
        # Apply gravity
        self.velocity.z += self.gravity
        # Age the particle
        self.age += 1
        # Fade alpha
        self.color = (self.color[0], self.color[1], self.color[2], 
                     max(0, self.color[3] - self.fade_rate))
        return self.age < self.lifetime
    
    def draw(self):
        if self.color[3] <= 0:
            return
            
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        glColor4f(self.color[0], self.color[1], self.color[2], self.color[3])
        glutSolidSphere(self.size, 6, 6)
        glPopMatrix()

class ExplosionEffect:
    def __init__(self, position, explosion_type='boom'):
        self.position = Vector3(position.x, position.y, position.z)
        self.explosion_type = explosion_type  # 'boom' or 'enemy_defeat'
        self.particles = []
        self.active = True
        self.age = 0
        self.max_age = 120  # 2 seconds at 60fps
        
        # Screen shake properties
        self.shake_intensity = 15 if explosion_type == 'boom' else 8
        self.shake_duration = 30 if explosion_type == 'boom' else 15
        self.shake_timer = 0
        
        # Scale based on explosion type
        self.scale_multiplier = 1.5 if explosion_type == 'boom' else 1.0
        
        self.create_particles()
        
    def create_particles(self):
        """Generate particles based on explosion type"""
        if self.explosion_type == 'boom':
            particle_count = 50
        elif self.explosion_type == 'warning':
            particle_count = 40
        elif self.explosion_type == 'muzzle_flash':
            particle_count = 20
        else:
            particle_count = 30
        
        for _ in range(particle_count):
            # Random direction and speed
            angle_h = random.uniform(0, 2 * math.pi)
            angle_v = random.uniform(-math.pi/4, math.pi/4)
            speed = random.uniform(5, 15) * self.scale_multiplier
            
            velocity = Vector3(
                math.cos(angle_h) * math.cos(angle_v) * speed,
                math.sin(angle_h) * math.cos(angle_v) * speed,
                math.sin(angle_v) * speed
            )
            
            # Color based on explosion type
            if self.explosion_type == 'boom':
                # Orange/red explosion
                color = (random.uniform(0.8, 1.0), random.uniform(0.3, 0.7), 0.1, 1.0)
            elif self.explosion_type == 'warning':
                # Bright red warning
                color = (1.0, random.uniform(0.0, 0.3), 0.0, 1.0)
            elif self.explosion_type == 'muzzle_flash':
                # Bright yellow/white muzzle flash
                color = (1.0, 1.0, random.uniform(0.5, 1.0), 1.0)
            else:
                # Blue/white enemy defeat
                color = (random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), 1.0, 1.0)
            
            # Particle properties
            size = random.uniform(2, 6) * self.scale_multiplier
            
            # Adjust lifetime based on explosion type
            if self.explosion_type == 'warning':
                lifetime = random.randint(60, 120)  # Longer for warning
            elif self.explosion_type == 'muzzle_flash':
                lifetime = random.randint(10, 30)   # Shorter for muzzle flash
            else:
                lifetime = random.randint(30, 80)
            
            # Add some position variation
            pos_offset = Vector3(
                random.uniform(-5, 5),
                random.uniform(-5, 5),
                random.uniform(-2, 8)
            )
            
            particle = Particle(
                self.position + pos_offset,
                velocity,
                color,
                size,
                lifetime
            )
            self.particles.append(particle)
    
    def update(self):
        """Update explosion effect"""
        if not self.active:
            return
            
        self.age += 1
        self.shake_timer += 1
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Check if explosion is finished
        if self.age >= self.max_age or len(self.particles) == 0:
            self.active = False
    
    def get_screen_shake(self):
        """Get current screen shake offset"""
        if self.shake_timer >= self.shake_duration:
            return Vector3(0, 0, 0)
            
        # Diminishing shake intensity
        intensity = self.shake_intensity * (1.0 - self.shake_timer / self.shake_duration)
        
        return Vector3(
            random.uniform(-intensity, intensity),
            random.uniform(-intensity, intensity),
            random.uniform(-intensity/2, intensity/2)
        )
    
    def draw(self):
        """Draw explosion particles"""
        if not self.active:
            return
            
        # Enable blending for particle effects
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for particle in self.particles:
            particle.draw()
            
        glDisable(GL_BLEND)

class CoverObject:
    def __init__(self, position, cover_type='wall'):
        self.position = Vector3(position.x, position.y, position.z)
        self.cover_type = cover_type  # 'wall', 'barrier', 'pillar'
        self.max_health = 100
        self.health = self.max_health
        self.destroyed = False
        self.damage_effects = []
        
        # Cover dimensions based on type
        if cover_type == 'wall':
            self.width = 80
            self.height = 60
            self.depth = 20
        elif cover_type == 'barrier':
            self.width = 60
            self.height = 40
            self.depth = 15
        elif cover_type == 'pillar':
            self.width = 30
            self.height = 80
            self.depth = 30
    
    def take_damage(self, damage_amount, impact_pos):
        if not self.destroyed:
            self.health -= damage_amount
            # Add damage effect at impact position
            self.damage_effects.append({
                'pos': Vector3(impact_pos.x, impact_pos.y, impact_pos.z),
                'time': 0,
                'max_time': 60
            })
            
            if self.health <= 0:
                self.destroyed = True
                return True  # Cover destroyed
        return False
    
    def update(self):
        # Update damage effects
        self.damage_effects = [effect for effect in self.damage_effects 
                              if effect['time'] < effect['max_time']]
        for effect in self.damage_effects:
            effect['time'] += 1
    
    def check_collision(self, point, radius=0):
        """Check if a point collides with this cover object"""
        if self.destroyed:
            return False
            
        half_w = self.width / 2 + radius
        half_h = self.height / 2 + radius
        half_d = self.depth / 2 + radius
        
        return (abs(point.x - self.position.x) < half_w and
                abs(point.y - self.position.y) < half_h and
                abs(point.z - self.position.z) < half_d)
    
    def provides_cover_for(self, player_pos, enemy_pos):
        """Check if this cover blocks line of sight between player and enemy"""
        if self.destroyed:
            return False
            
        # Simple line-box intersection check
        # Check if the line from enemy to player intersects with cover bounds
        direction = player_pos - enemy_pos
        length = math.sqrt(direction.x**2 + direction.y**2 + direction.z**2)
        
        if length == 0:
            return False
            
        direction = Vector3(direction.x/length, direction.y/length, direction.z/length)
        
        # Check multiple points along the line
        for i in range(int(length)):
            check_point = enemy_pos + (direction * i)
            if self.check_collision(check_point, 10):
                return True
        return False
    
    def draw(self):
        if self.destroyed:
            return
            
        glPushMatrix()
        glTranslatef(self.position.x, self.position.y, self.position.z)
        
        # Color based on health
        health_ratio = self.health / self.max_health
        if self.cover_type == 'wall':
            glColor3f(0.6 * health_ratio, 0.6 * health_ratio, 0.6 * health_ratio)
        elif self.cover_type == 'barrier':
            glColor3f(0.8 * health_ratio, 0.4 * health_ratio, 0.2 * health_ratio)
        elif self.cover_type == 'pillar':
            glColor3f(0.5 * health_ratio, 0.7 * health_ratio, 0.5 * health_ratio)
        
        # Draw main cover object
        glPushMatrix()
        glScalef(self.width/30, self.height/30, self.depth/30)
        glutSolidCube(30)
        glPopMatrix()
        
        # Draw damage effects
        for effect in self.damage_effects:
            glPushMatrix()
            effect_pos = effect['pos'] - self.position
            glTranslatef(effect_pos.x, effect_pos.y, effect_pos.z)
            
            # Fading damage mark
            alpha = 1.0 - (effect['time'] / effect['max_time'])
            glColor3f(1.0 * alpha, 0.2 * alpha, 0.0 * alpha)
            glutSolidSphere(3, 6, 6)
            glPopMatrix()
        
        glPopMatrix()

class CoverSystem:
    def __init__(self):
        self.covers = []
        self.initialize_covers()
    
    def initialize_covers(self):
        """Place cover objects strategically around the map"""
        # Walls
        self.covers.append(CoverObject(Vector3(-200, 0, 30), 'wall'))
        self.covers.append(CoverObject(Vector3(200, 0, 30), 'wall'))
        self.covers.append(CoverObject(Vector3(0, -200, 30), 'wall'))
        self.covers.append(CoverObject(Vector3(0, 200, 30), 'wall'))
        
        # Barriers
        self.covers.append(CoverObject(Vector3(-100, -100, 20), 'barrier'))
        self.covers.append(CoverObject(Vector3(100, 100, 20), 'barrier'))
        self.covers.append(CoverObject(Vector3(-100, 100, 20), 'barrier'))
        self.covers.append(CoverObject(Vector3(100, -100, 20), 'barrier'))
        
        # Pillars
        self.covers.append(CoverObject(Vector3(-150, -150, 40), 'pillar'))
        self.covers.append(CoverObject(Vector3(150, 150, 40), 'pillar'))
        self.covers.append(CoverObject(Vector3(-150, 150, 40), 'pillar'))
        self.covers.append(CoverObject(Vector3(150, -150, 40), 'pillar'))
    
    def update(self):
        for cover in self.covers:
            cover.update()
    
    def check_projectile_collision(self, projectile_pos, projectile_radius=5):
        """Check if projectile hits any cover"""
        for cover in self.covers:
            if cover.check_collision(projectile_pos, projectile_radius):
                return cover
        return None
    
    def get_cover_for_player(self, player_pos, enemy_pos):
        """Find cover that protects player from enemy"""
        for cover in self.covers:
            if cover.provides_cover_for(player_pos, enemy_pos):
                return cover
        return None
    
    def draw(self):
        for cover in self.covers:
            cover.draw()

class GameRenderer:
    def __init__(self):
        self.grid_length = 600
    
    def draw_text(self, x, y, text, font=GLUT_BITMAP_HELVETICA_18):

        glColor3f(0.0, 1.0, 0.0) 
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 1000, 0, 800)
        
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))
        
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    
    def draw_grid(self):

        grid_size = 60
        for i in range(-self.grid_length//grid_size, self.grid_length//grid_size + 1):
            for j in range(-self.grid_length//grid_size, self.grid_length//grid_size + 1):
                x1 = i * grid_size
                y1 = j * grid_size
                x2 = x1 + grid_size
                y2 = y1 + grid_size
                
                if (i + j) % 2 == 0:
                    glColor3f(1.0, 1.0, 1.0)  
                else:
                    glColor3f(0.7, 0.5, 0.95)
                
                glBegin(GL_QUADS)
                glVertex3f(x1, y1, 0)
                glVertex3f(x2, y1, 0)
                glVertex3f(x2, y2, 0)
                glVertex3f(x1, y2, 0)
                glEnd()
        
        glColor3f(0.0, 0.0, 1.0) 
        wall_height = 120
        
        glBegin(GL_QUADS)
        glVertex3f(-self.grid_length, self.grid_length, 0)
        glVertex3f(self.grid_length, self.grid_length, 0)
        glVertex3f(self.grid_length, self.grid_length, wall_height)
        glVertex3f(-self.grid_length, self.grid_length, wall_height)
        glEnd()
        
        glBegin(GL_QUADS)
        glVertex3f(-self.grid_length, -self.grid_length, 0)
        glVertex3f(self.grid_length, -self.grid_length, 0)
        glVertex3f(self.grid_length, -self.grid_length, wall_height)
        glVertex3f(-self.grid_length, -self.grid_length, wall_height)
        glEnd()
        
        glBegin(GL_QUADS)
        glVertex3f(-self.grid_length, -self.grid_length, 0)
        glVertex3f(-self.grid_length, self.grid_length, 0)
        glVertex3f(-self.grid_length, self.grid_length, wall_height)
        glVertex3f(-self.grid_length, -self.grid_length, wall_height)
        glEnd()
        
        glBegin(GL_QUADS)
        glVertex3f(self.grid_length, -self.grid_length, 0)
        glVertex3f(self.grid_length, self.grid_length, 0)
        glVertex3f(self.grid_length, self.grid_length, wall_height)
        glVertex3f(self.grid_length, -self.grid_length, wall_height)
        glEnd()

class Game:
    def __init__(self):
        self.player = Player()
        self.camera = Camera()
        self.renderer = GameRenderer()
        # self.skybox = Skybox()

        # Lighting system removed
        self.power_up_system = PowerUpSystem()
        self.cover_system = CoverSystem()
        self.bomb_system = BombSystem()
        self.avatar = Avatar(Vector3(100, 100, 25))  # Avatar positioned in the game world
        self.bullets = []
        self.enemies = []
        
        self.game_over = False
        self.player_life = 5
        self.game_score = 0
        self.bullets_missed = 0
        self.max_bullets_missed = 10
        self.player_bullets = 30  # Starting bullets for player
        
        self.cheat_mode = False
        self.auto_rotate_angle = 0
        
        # Countdown timer system
        self.countdown_timer = 30.0  # 30 seconds default
        self.max_countdown_timer = 30.0
        self.timer_active = True
        
        # Explosion state tracking
        self.explosion_active = False
        self.explosion_timer = 0
        self.explosion_duration = 120  # 2 seconds at 60 FPS
        
        # Explosion effects system
        self.explosion_effects = []
        self.screen_shake_offset = Vector3(0, 0, 0)
        
        # Coordinated attack system
        self.enemies_eliminated = 0
        self.coordinated_attack_active = False
        self.coordinated_attack_warning = False
        self.warning_timer = 0
        self.warning_duration = 120  # 2 seconds warning
        self.coordinated_attack_triggered = False
        
        self.initialize_enemies()
        self.bomb_system.initialize_bombs()
    
    def initialize_enemies(self):
  
        self.enemies.clear()
        grid_size = 60
        spawn_positions = [
            Vector3(-300, 300, 25), 
            Vector3(300, 300, 25),  
            Vector3(-300, -300, 25),
            Vector3(300, -300, 25), 
            Vector3(0, 360, 25)     
        ]
        
        for pos in spawn_positions:
            self.enemies.append(AIEnemy(pos))
    
    def spawn_enemy_at_random_position(self):
  
        grid_size = 60
        grid_x = random.randint(-9, 9)  
        grid_y = random.randint(-9, 9)
        
        x = grid_x * grid_size
        y = grid_y * grid_size
        z = 25
        
        return AIEnemy(Vector3(x, y, z))
    
    def fire_bullet(self):
  
        if self.game_over:
            return False
        
        gun_tip = self.player.get_gun_tip_position()
        direction = self.player.get_gun_direction()
        bullet = Bullet(gun_tip, direction)
        self.bullets.append(bullet)
        print("Player Bullet Fired!")
        return True
    
    def can_hit_enemy_precisely(self, direction):
  
        gun_tip = self.player.get_gun_tip_position()
        
        for enemy in self.enemies:
            to_enemy = enemy.position - gun_tip
            distance = math.sqrt(to_enemy.x**2 + to_enemy.y**2)
            
            if distance > 0:
                to_enemy_normalized = to_enemy.normalize()
                
                dot_product = (direction.x * to_enemy_normalized.x + 
                             direction.y * to_enemy_normalized.y)
                
                angle_to_enemy = math.degrees(math.atan2(to_enemy.y, to_enemy.x))
                current_angle = math.degrees(math.atan2(direction.y, direction.x))
                
                angle_to_enemy = (angle_to_enemy + 90) % 360  
                current_angle = (current_angle + 90) % 360

                angle_diff = abs(angle_to_enemy - current_angle)
                if angle_diff > 180:
                    angle_diff = 360 - angle_diff
                
                if dot_product > 0.98 and angle_diff < 5: 
                    return True
        return False
    
    def update_bullets(self):
        # Check bullet-bomb collisions first
        hit_bullets, destroyed_bombs = self.bomb_system.check_bullet_collisions(self.bullets)
        
        # Log destroyed bombs and create explosion effects
        for bomb in destroyed_bombs:
            print(f"Bomb exploded from bullet hits at {bomb.position.x}, {bomb.position.y}")
            # Create explosion effect at bomb position
            explosion = ExplosionEffect(bomb.position, 'boom')
            self.explosion_effects.append(explosion)
        
        # Remove hit bullets
        for bullet in hit_bullets:
            if bullet in self.bullets:
                self.bullets.remove(bullet)
        
        # Update remaining bullets
        for bullet in self.bullets[:]:
            if not bullet.update(self.cover_system):
                self.bullets.remove(bullet)
                self.bullets_missed += 1
                print(f"Bullet missed: {self.bullets_missed}")
                continue
            
            for enemy in self.enemies[:]:
                if enemy.check_collision(bullet):
                    # Create explosion effect at enemy position
                    explosion = ExplosionEffect(enemy.position, 'enemy_defeat')
                    self.explosion_effects.append(explosion)
                    
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.enemies.append(self.spawn_enemy_at_random_position())
                    self.game_score += 1
                    self.enemies_eliminated += 1
                    
                    # Add 5 seconds to timer as reward for killing enemy
                    if self.timer_active:
                        self.countdown_timer += 5.0
                        if self.countdown_timer > self.max_countdown_timer:
                            self.countdown_timer = self.max_countdown_timer
                    
                    print(f"Enemy hit! Score: {self.game_score}, Eliminated: {self.enemies_eliminated}")
                    
                    # Check for coordinated attack trigger
                    if self.enemies_eliminated >= 5 and not self.coordinated_attack_triggered:
                        self.trigger_coordinated_attack_warning()
                    
                    break
    
    def trigger_coordinated_attack_warning(self):
        """Trigger warning phase before coordinated attack"""
        self.coordinated_attack_warning = True
        self.warning_timer = 0
        self.coordinated_attack_triggered = True
        print("WARNING: Coordinated enemy attack incoming!")
        
        # Create warning explosion effects
        for enemy in self.enemies:
            warning_explosion = ExplosionEffect(enemy.position, 'warning')
            self.explosion_effects.append(warning_explosion)
    
    def execute_coordinated_attack(self):
        """Execute the coordinated attack - all enemies fire simultaneously"""
        self.coordinated_attack_active = True
        self.coordinated_attack_warning = False
        
        print("COORDINATED ATTACK EXECUTED!")
        
        # Make all enemies fire at the player simultaneously
        for enemy in self.enemies:
            # Force enemy to fire with high accuracy
            enemy.fire_at_target(accuracy_penalty=0.1)  # Very accurate shots
            
            # Create muzzle flash effect
            muzzle_flash = ExplosionEffect(enemy.position, 'muzzle_flash')
            self.explosion_effects.append(muzzle_flash)
        
        # Reset elimination counter for next coordinated attack
        self.enemies_eliminated = 0
        self.coordinated_attack_triggered = False
    
    def update_coordinated_attack_system(self):
        """Update the coordinated attack warning and execution"""
        if self.coordinated_attack_warning:
            self.warning_timer += 1
            
            # Execute attack after warning period
            if self.warning_timer >= self.warning_duration:
                self.execute_coordinated_attack()
        
        # Reset coordinated attack state after a brief period
        if self.coordinated_attack_active:
            # Allow some time for projectiles to travel
            if self.warning_timer >= self.warning_duration + 30:  # 0.5 seconds after attack
                self.coordinated_attack_active = False
                self.warning_timer = 0
    
    def update_enemies(self):
        # Update coordinated attack system
        self.update_coordinated_attack_system()
        
        # Update player's cover status
        self.player.check_cover_status(self.cover_system, self.enemies)
        
        for enemy in self.enemies:
            # Pass player object and cover system to enemy update
            enemy.update(self.player, self.cover_system)
            
            # Check projectile collisions with cover
            enemy.check_projectile_collisions_with_cover(self.cover_system)
            
            # Check projectile collisions with player
            if enemy.check_projectile_collisions_with_player(self.player):
                # If coordinated attack is active, instant game over
                if self.coordinated_attack_active:
                    self.player_life = 0
                    print("GAME OVER! Hit by coordinated attack!")
                else:
                    self.player_life -= 1
                    print(f"Player hit by projectile! Life remaining: {self.player_life}")
            
            # Check direct collision with enemy (melee range)
            distance = enemy.position.distance_to(self.player.position)
            if distance < 40:  
                self.player_life -= 1
                print(f"Player hit by enemy! Life remaining: {self.player_life}")
                new_enemy = self.spawn_enemy_at_random_position()
                enemy.position = new_enemy.position
                enemy.original_position = new_enemy.original_position
    
    def update_cheat_mode(self):
  
        if not self.cheat_mode:
            return
        
        self.auto_rotate_angle += 1
        if self.auto_rotate_angle >= 360:
            self.auto_rotate_angle = 0
        
        self.player.angle = self.auto_rotate_angle
        
        direction = self.player.get_gun_direction()
        if self.can_hit_enemy_precisely(direction):
            current_time = glutGet(GLUT_ELAPSED_TIME)
            if not hasattr(self, 'last_cheat_shot_time'):
                self.last_cheat_shot_time = 0
            
            if current_time - self.last_cheat_shot_time > 500: 
                self.fire_bullet()
                self.last_cheat_shot_time = current_time
    
    def check_power_up_collisions(self):
        collected_powers = self.power_up_system.check_collisions(self.player)
        
        for power_type in collected_powers:
            if power_type == 'health':
                self.player_life = min(self.player_life + 1, 10)  # Max 10 lives
                print(f"Health power-up collected! Life: {self.player_life}")
            elif power_type == 'speed':
                # Temporary speed boost could be implemented
                print("Speed power-up collected!")
            elif power_type == 'damage':
                # Damage boost could be implemented
                print("Damage power-up collected!")
            elif power_type == 'shield':
                # Shield effect could be implemented
                print("Shield power-up collected!")
            elif power_type == 'bullet':
                # Add 5 bullets to player's ammunition
                self.player_bullets += 5
                print(f"Bullet power-up collected! Bullets: {self.player_bullets}")
    
    def check_bomb_collisions(self):
        if not self.explosion_active:  # Only check if not already exploding
            exploded_bombs = self.bomb_system.check_collisions(self.player)
            if exploded_bombs:
                for bomb in exploded_bombs:
                    print("BOOM! Player hit by bomb!")
                    # Create explosion effect at bomb position
                    explosion = ExplosionEffect(bomb.position, 'boom')
                    self.explosion_effects.append(explosion)
                
                # Start explosion sequence
                self.explosion_active = True
                self.explosion_timer = 0
                self.game_over = True
                self.player.lie_down()  # Make player fall down
                print("You have exploded!")
    
    def check_game_over(self):
  
        if self.player_life <= 0 or self.bullets_missed >= self.max_bullets_missed:
            self.game_over = True
            self.player.lie_down()
            print("Game Over!")
    
    def reset_game(self):
  
        self.game_over = False
        self.player_life = 5
        self.game_score = 0
        self.bullets_missed = 0
        self.player_bullets = 30  # Reset bullets
        self.cheat_mode = False
        self.auto_rotate_angle = 0
        
        # Reset countdown timer
        self.countdown_timer = 30.0
        self.timer_active = True
        
        # Reset explosion state
        self.explosion_active = False
        self.explosion_timer = 0
        
        # Reset coordinated attack system
        self.enemies_eliminated = 0
        self.coordinated_attack_active = False
        self.coordinated_attack_warning = False
        self.warning_timer = 0
        self.coordinated_attack_triggered = False
        
        # Clear explosion effects
        self.explosion_effects.clear()
        self.screen_shake_offset = Vector3(0, 0, 0)
        
        self.player.reset()
        self.bullets.clear()
        self.bomb_system.clear_all()
        self.bomb_system.initialize_bombs()
        self.initialize_enemies()
        print("Game Reset!")
    
    def update_explosion_effects(self):
        """Update all explosion effects and calculate screen shake"""
        # Reset screen shake
        self.screen_shake_offset = Vector3(0, 0, 0)
        
        # Update explosion effects
        active_explosions = []
        for explosion in self.explosion_effects:
            explosion.update()
            if explosion.active:
                active_explosions.append(explosion)
                # Accumulate screen shake from all active explosions
                shake = explosion.get_screen_shake()
                self.screen_shake_offset = self.screen_shake_offset + shake
        
        self.explosion_effects = active_explosions
    
    def update(self):
        if not self.game_over:
            self.player.update_movement(self.cover_system, self.enemies)  # Update player movement with collision detection
            # self.skybox.update()

            # Lighting update removed
            self.power_up_system.update()
            self.cover_system.update()
            self.bomb_system.update()
            self.avatar.update()  # Update avatar animation
            self.update_bullets()
            self.update_enemies()
            self.check_power_up_collisions()
            self.check_bomb_collisions()
            self.update_cheat_mode()
            self.check_game_over()
            
            # Update explosion effects and calculate screen shake
            self.update_explosion_effects()
            
            # Update countdown timer
            if self.timer_active:
                self.countdown_timer -= 1.0/60.0  # Decrease by 1/60 second per frame (assuming 60 FPS)
                if self.countdown_timer <= 0:
                    self.countdown_timer = 0
                    self.timer_active = False
                    self.game_over = True  # Trigger game over when timer reaches zero
        elif self.explosion_active:
            # Update explosion timer
            self.explosion_timer += 1
            # Explosion animation completes after duration
            if self.explosion_timer >= self.explosion_duration:
                self.explosion_active = False
    
    def render(self):
  
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, 1000, 800)

        self.camera.setup(self.player, self.screen_shake_offset)
        # Lighting application removed

        # self.skybox.draw()
        self.renderer.draw_grid()
        self.player.draw()
        
        for enemy in self.enemies:
            enemy.draw()
        
        for bullet in self.bullets:
            bullet.draw()
        
        # Draw explosion effects
        for explosion in self.explosion_effects:
            explosion.draw()

        # Light sources drawing removed
        self.power_up_system.draw()
        self.cover_system.draw()
        self.bomb_system.draw()
        self.avatar.draw()  # Draw avatar with face rotation
        
        # Lighting system removed - no need to disable
        self.renderer.draw_text(10, 770, f"Player Life Remaining: {self.player_life}")
        self.renderer.draw_text(10, 740, f"Game Score: {self.game_score}")
        self.renderer.draw_text(10, 710, f"Player Bullet Missed: {self.bullets_missed}")
        self.renderer.draw_text(10, 680, f"Bullets Remaining: {self.player_bullets}")
        
        if self.game_over:
            if self.explosion_active:
                # Show explosion message during animation
                self.renderer.draw_text(350, 400, "EXPLOSION IN PROGRESS...")
            else:
                # Show final message after explosion completes
                self.renderer.draw_text(320, 420, "You have exploded!")
                self.renderer.draw_text(300, 380, "Press R to restart the game")
        
        if self.cheat_mode:
            self.renderer.draw_text(10, 650, "CHEAT MODE: ON")
        
        camera_mode = "First Person" if self.camera.first_person else "Third Person"
        self.renderer.draw_text(10, 620, f"Camera: {camera_mode}")
        
        # Draw countdown timer on the right side of the screen
        timer_text = f"Time: {int(self.countdown_timer)}s"
        self.renderer.draw_text(850, 770, timer_text)
        
        # Draw timer bar for visual representation
        timer_percentage = self.countdown_timer / self.max_countdown_timer
        bar_width = 120
        bar_height = 10
        bar_x = 850
        bar_y = 750
        
        # Draw timer bar background (red)
        glColor3f(0.8, 0.2, 0.2)
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + bar_width, bar_y)
        glVertex2f(bar_x + bar_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        
        # Draw timer bar fill (green to red gradient based on time remaining)
        if timer_percentage > 0.5:
            glColor3f(0.2, 0.8, 0.2)  # Green when time is good
        elif timer_percentage > 0.25:
            glColor3f(0.8, 0.8, 0.2)  # Yellow when time is medium
        else:
            glColor3f(0.8, 0.2, 0.2)  # Red when time is low
            
        fill_width = bar_width * timer_percentage
        glBegin(GL_QUADS)
        glVertex2f(bar_x, bar_y)
        glVertex2f(bar_x + fill_width, bar_y)
        glVertex2f(bar_x + fill_width, bar_y + bar_height)
        glVertex2f(bar_x, bar_y + bar_height)
        glEnd()
        
        # Draw coordinated attack warnings and status
        if self.coordinated_attack_warning:
            # Flashing warning message
            if (self.warning_timer // 10) % 2 == 0:  # Flash every 10 frames
                self.renderer.draw_text(250, 450, "!!! COORDINATED ATTACK INCOMING !!!")
                self.renderer.draw_text(300, 420, "TAKE COVER IMMEDIATELY!")
            
            # Warning countdown
            warning_time_left = (self.warning_duration - self.warning_timer) / 60.0
            self.renderer.draw_text(350, 390, f"Attack in: {warning_time_left:.1f}s")
            
        elif self.coordinated_attack_active:
            # Attack in progress message
            self.renderer.draw_text(280, 450, "COORDINATED ATTACK IN PROGRESS!")
            self.renderer.draw_text(320, 420, "AVOID ALL PROJECTILES!")
        
        # Display enemy elimination counter
        self.renderer.draw_text(10, 590, f"Enemies Eliminated: {self.enemies_eliminated}/5")
        if self.enemies_eliminated >= 5 and not self.coordinated_attack_triggered:
            self.renderer.draw_text(10, 560, "Next elimination triggers attack!")

        glutSwapBuffers()

game = None

def keyboard_listener(key, x, y):
    global game
    
    if key == b'r':
        game.reset_game()
        return
    
    if game.game_over:
        return
    
    # Movement controls - diagonal movement support
    if key == b'w':
        game.player.set_movement_key('forward', True)
    elif key == b's':
        game.player.set_movement_key('backward', True)
    elif key == b'a':
        if game.cheat_mode:
            game.player.set_movement_key('left', True)
        else:
            game.player.aim_gun_left()  # Gun aiming
    elif key == b'd':
        if game.cheat_mode:
            game.player.set_movement_key('right', True)
        else:
            game.player.aim_gun_right()  # Gun aiming
    elif key == b'q':  # Strafe left
        game.player.set_movement_key('left', True)
    elif key == b'e':  # Strafe right
        game.player.set_movement_key('right', True)
    elif key == b'z':  # Rotate body left
        game.player.rotate_left()
    elif key == b'x':  # Rotate body right
        game.player.rotate_right()
    elif key == b'c':
        game.cheat_mode = not game.cheat_mode
        print(f"Cheat mode: {'ON' if game.cheat_mode else 'OFF'}")
    elif key == b'f':  # Trigger avatar face rotation
        game.avatar.trigger_face_rotation()
        print("Avatar face rotation triggered!")
    elif key == b'\x11':  # Ctrl+Q for crouch
        game.player.crouch()

def keyboard_up_listener(key, x, y):
    """Handle key release events for smooth movement"""
    global game
    
    if game.game_over:
        return
    
    # Release movement keys
    if key == b'w':
        game.player.set_movement_key('forward', False)
    elif key == b's':
        game.player.set_movement_key('backward', False)
    elif key == b'q':
        game.player.set_movement_key('left', False)
    elif key == b'e':
        game.player.set_movement_key('right', False)
    elif key == b'a' and game.cheat_mode:
        game.player.set_movement_key('left', False)
    elif key == b'd' and game.cheat_mode:
        game.player.set_movement_key('right', False)

def special_key_listener(key, x, y):
    global game
    
    if key == GLUT_KEY_UP:
        game.camera.move_up()
    elif key == GLUT_KEY_DOWN:
        game.camera.move_down()
    elif key == GLUT_KEY_LEFT:
        game.camera.rotate_left()
    elif key == GLUT_KEY_RIGHT:
        game.camera.rotate_right()

def mouse_listener(button, state, x, y):
    global game
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        game.fire_bullet()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        game.camera.toggle_first_person()
        mode = "First Person" if game.camera.first_person else "Third Person"
        print(f"Camera mode: {mode}")

def idle():
    global game
    game.update()
    glutPostRedisplay()

def display():
    global game
    game.render()

def main():
    global game
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    window = glutCreateWindow(b"Bullet Frenzy - 3D Game (OOP Version)")

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    
    game = Game()

    glutDisplayFunc(display)
    glutKeyboardFunc(keyboard_listener)
    glutKeyboardUpFunc(keyboard_up_listener)
    glutSpecialFunc(special_key_listener)
    glutMouseFunc(mouse_listener)
    glutIdleFunc(idle)

    print("=== BULLET FRENZY CONTROLS ===")
    print("WASD: Move (W=forward, S=backward, Q=left, E=right)")
    print("A/D: Aim gun left/right (360-degree aiming)")
    print("Z/X: Rotate player body left/right")
    print("Ctrl+Q: Crouch (harder to detect, reduced accuracy)")
    print("Left Click: Fire bullet")
    print("Right Click: Toggle camera mode")
    print("Arrow Keys: Move/rotate camera")
    print("C: Toggle cheat mode (auto-aim and shoot)")
    print("R: Restart game")
    print("===============================")
    print("Game started! Use diagonal movement and 360-degree aiming!")

    glutMainLoop()

if __name__ == "__main__":
    main()