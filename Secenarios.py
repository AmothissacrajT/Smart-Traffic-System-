import pygame
import time
import random

scenerio = 1
# Initialize pygame

pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Four-Way Traffic Simulation")

# Colors
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
CYAN = (0, 255, 255)  # EV Color
PURPLE = (128, 0, 128)  # AV Color
ORANGE = (255, 165, 0)  # Emergency Vehicle Color
NORMAL_VEHICLE = (200, 200, 0)


background_image = pygame.image.load(r"C:\Users\Amoth issac raj\OneDrive\Desktop\Blaze trial 1.0\Images\intersection.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))


# Traffic light properties1
if scenerio in [1,0]:
    signal_states = {"North": GREEN, "South": RED, "East": RED, "West": RED}
elif scenerio in [2,3]:
    signal_states = {"North": RED, "South": RED, "East": GREEN, "West": RED}

signal_timer = time.time()
signal_duration = 2  # Change signal every 10 seconds

# Lane positions to define lane boundaries (the white lines)
LANE_POSITIONS = {
    "right": [260, 300],  # Positions for right-moving vehicles
    "left": [370, 410],   # Positions for left-moving vehicles
    "up": [380, 430],     # Positions for up-moving vehicles
    "down": [490, 530]    # Positions for down-moving vehicles
}

MAX_VEHICLES = 15  # Maximum number of vehicles on screen at once
SAFE_DISTANCE = 20
index=0

# Load vehicle images
VEHICLE_IMAGES = {
    "Emergency": pygame.image.load(r"C:\Users\Amoth issac raj\OneDrive\Desktop\Blaze trial 1.0\Images\Ambulance.png-removebg-preview.png"),
    "EV": pygame.image.load(r"C:\Users\Amoth issac raj\OneDrive\Desktop\Blaze trial 1.0\Images\Ev.png-removebg-preview.png"),
    "AV": pygame.image.load(r"C:\Users\Amoth issac raj\OneDrive\Desktop\Blaze trial 1.0\Images\av.png-removebg-preview.png"),
    "Normal": pygame.image.load(r"C:\Users\Amoth issac raj\OneDrive\Desktop\Blaze trial 1.0\Images\car.png-removebg-preview.png")
}

class Vehicle:
    def __init__(self, x, y, vehicle_type, direction, index):
        
        self.width = 50
        self.height = 50
        
        self.speed = 2
        self.vehicle_type = vehicle_type
        self.direction = direction
        self.index = index
        if scenerio == 2:
            self.battery = random.randint(5,20) if vehicle_type == "EV" else None  # Only EVs have a battery
        else:
            self.battery = random.randint(20,100) if vehicle_type == "EV" else None  # Only EVs have a battery

        if vehicle_type in ["Emergency"]:
            self.priority = 500 # Priority for EVs and AVs
        elif vehicle_type in ["EV"] and self.battery < 30:
            self.priority = 3
        elif vehicle_type in ["EV","AV"]:
            self.priority = 2
        elif vehicle_type == "Normal":
            self.priority = 1

        # Load and scale the vehicle image
        self.image = pygame.transform.scale(VEHICLE_IMAGES[vehicle_type], (self.width, self.height))
        # Rotate the image based on direction
        if direction == "left":
            self.image = pygame.transform.rotate(self.image, 90)
        elif direction == "right":
            self.image = pygame.transform.rotate(self.image, -90)
        elif direction == "down":
            self.image = pygame.transform.rotate(self.image, 180)
        
        # Spawn the vehicle in between the white lines (the lanes)
        self.lane = random.choice(LANE_POSITIONS[direction])
        self.has_crossed_junction = False  # Track if the vehicle has crossed the junction
        self.has_crossed = False

        if direction in ["right", "left"]:
            self.y = self.lane
            self.x = x if direction == "right" else WIDTH - x
        else:
            self.x = self.lane
            self.y = y if direction == "down" else HEIGHT - y

        self.queue_position = None  # Position in the queue (if applicable)

    def move(self, vehicles):
        """Move the vehicle, with queueing logic for red lights"""
        # Check if the vehicle should stop at the intersection due to a red light
        if self.direction == "right" and signal_states["East"] == RED:
            if self.x <= 360 and self.x >= 330:  # Crossing the intersection area
                self.queue_position = True  # Vehicle is waiting in the queue
                self.follow_queue(vehicles, signal_states["East"])  # Stay in the queue until the car in front moves
                if self.x > 360 :
                    pass
                else:
                    self.speed = 0  # Vehicle stays in place
        elif self.direction == "left" and signal_states["West"] == RED:
            if self.x >= 580 and self.x <= 610:  # Crossing the intersection area
                self.queue_position = True  # Vehicle is waiting in the queue
                self.follow_queue(vehicles, signal_states["West"])  # Stay in the queue until the car in front moves
                if self.x < 580:
                    pass
                else:
                    self.speed = 0  # Vehicle stays in place
        
        elif self.direction == "down" and signal_states["South"] == RED:
            if self.y <= 240 and self.y >= 200:  # Crossing the intersection area
                self.queue_position = True  # Vehicle is waiting in the queue
                self.follow_queue(vehicles, signal_states["South"])  # Stay in the queue until the car in front moves
                if self.y > 240:
                    pass
                else:
                    self.speed = 0  # Vehicle stays in place
        elif self.direction == "up" and signal_states["North"] == RED:
            if self.y >= 460 and self.y <= 490:  # Crossing the intersection area
                self.queue_position = True  # Vehicle is waiting in the queue
                self.follow_queue(vehicles, signal_states["North"])  # Stay in the queue until the car in front moves
                if self.y > 460:
                    pass
                else:
                    self.speed = 0  # Vehicle stays in place

        if self.vehicle_type == "EV" and self.battery > 0:
            self.battery -= 0.01  # Decrease battery for EV vehicle


        # Check for vehicles blocking the intersection
        def is_blocked_by_other_vehicle(x_min, x_max, y_min, y_max):
            for vehicle in vehicles:
                if vehicle != self and vehicle.x >= x_min and vehicle.x <= x_max and vehicle.y >= y_min and vehicle.y <= y_max:
                    return True  # There's another vehicle blocking the intersection
            return False  # No vehicle in the way

        # Check if the vehicle should stop due to a red light or a blocked intersection
        if self.direction == "right" and signal_states["East"] == GREEN:
            # Vehicle moving right should wait if there are vehicles in front (up/down vehicles) in the intersection
            if is_blocked_by_other_vehicle(330, 610, 210, 490):
                self.speed = 0  # Vehicle stops until the intersection clears
            else:
                self.speed = 2  # Vehicle moves if there's no blockage

        elif self.direction == "left" and signal_states["West"] == GREEN:
            # Vehicle moving left should wait if there are vehicles in front (up/down vehicles) in the intersection
            if is_blocked_by_other_vehicle(580, 610, 210, 490):
                self.speed = 0  # Vehicle stops until the intersection clears
            else:
                self.speed = 2  # Vehicle moves if there's no blockage

        elif self.direction == "down" and signal_states["South"] == GREEN:
            # Vehicle moving down should wait if there are vehicles in front (right/left vehicles) in the intersection
            if is_blocked_by_other_vehicle(330, 610, 320, 350):
                self.speed = 0  # Vehicle stops until the intersection clears
            else:
                self.speed = 2  # Vehicle moves if there's no blockage

        elif self.direction == "up" and signal_states["North"] == GREEN:
            # Vehicle moving up should wait if there are vehicles in front (right/left vehicles) in the intersection
            if is_blocked_by_other_vehicle(330, 610, 210, 240):
                self.speed = 0  # Vehicle stops until the intersection clears
            else:
                self.speed = 2  # Vehicle moves if there's no blockage

        # If the light is green and there's space, vehicle will move
        if self.queue_position is None:  # No longer in queue
            self.speed = 2  # Reset to default speed

        self.update_position(vehicles)  # Update position after moving

        # Check if the vehicle has crossed the junction
        if self.direction == "right" and self.x >= 500:
            self.has_crossed_junction = True
        elif self.direction == "left" and self.x <= 360:
            self.has_crossed_junction = True
        elif self.direction == "down" and self.y >= 460:
            self.has_crossed_junction = True
        elif self.direction == "up" and self.y <= 200:
            self.has_crossed_junction = True

        if self.direction == "right" and self.x >= WIDTH:
            self.has_crossed = True
        elif self.direction == "left" and self.x <= 0:
            self.has_crossed = True
        elif self.direction == "down" and self.y >= HEIGHT:
            self.has_crossed = True
        elif self.direction == "up" and self.y <= 0:
            self.has_crossed = True

        

        
    
    def update_position(self, vehicles):
        """Update position with safe distance check"""
        if self.direction == "right":
            # Check for vehicle ahead in the same lane
            
                
            for vehicle in vehicles:
                if vehicle.direction in ["up","down"] and vehicle.y >= 240 and vehicle.y <= 360 and self.has_crossed_junction == False:
                    if self.x <= 360 and self.x >= 330:
                        self.speed=0 

                if vehicle != self and vehicle.direction == "right" and vehicle.y == self.y:  # Same lane
                    if vehicle.x > self.x and vehicle.x - self.x < self.width + SAFE_DISTANCE:
                        # Slow down if the vehicle ahead is too close 
                        self.speed = max(0, vehicle.speed * 0.75)  # Reduce speed, but not to zero
                        break
                
            # Move the vehicle if there is enough space
            self.x += self.speed
            if self.x >= WIDTH:
                self.has_crossed_junction = False  # Wrap around to the start

        elif self.direction == "left":
            # Check for vehicle ahead in the same lane
            for vehicle in vehicles:
                if vehicle.direction in ["up","down"] and vehicle.y >= 240 and vehicle.y <= 380 and self.has_crossed_junction == False:
                    if self.x >= 580 and self.x <= 610:
                        self.speed=0 

                if vehicle != self and vehicle.direction == "left" and vehicle.y == self.y:  # Same lane
                    if self.x > vehicle.x and self.x - vehicle.x < self.width + SAFE_DISTANCE:
                        # Slow down if the vehicle ahead is too close
                        self.speed = max(0, vehicle.speed * 0.75)  # Reduce speed, but not to zero
                        break
            # Move the vehicle if there is enough space
            self.x -= self.speed
            if self.x <= 0:
                self.has_crossed_junction = False  # Wrap around to the start

        elif self.direction == "down":
            # Check for vehicle ahead in the same lane
            for vehicle in vehicles:
                if vehicle.direction in ["right","left"] and vehicle.x >= 400 and vehicle.x <= 550 and self.has_crossed_junction == False:
                    if self.y <= 240 and self.y >= 210:
                        self.speed=0 

                if vehicle != self and vehicle.direction == "down" and vehicle.x == self.x:  # Same lane
                    if vehicle.y > self.y and vehicle.y - self.y < self.height + SAFE_DISTANCE:
                        # Slow down if the vehicle ahead is too close
                        self.speed = max(0, vehicle.speed * 0.75)  # Reduce speed, but not to zero
                        break
            # Move the vehicle if there is enough space
            self.y += self.speed
            if self.y >= HEIGHT:
                self.has_crossed_junction = False  # Wrap around to the start

        elif self.direction == "up":
            # Check for vehicle ahead in the same lane
            for vehicle in vehicles:
                if vehicle.direction in ["right","left"] and vehicle.x >= 400 and vehicle.x <= 550 and self.has_crossed_junction == False:
                    if self.y >= 460 and self.y <= 490:
                        self.speed=0 

                if vehicle != self and vehicle.direction == "up" and vehicle.x == self.x:  # Same lane
                    if self.y > vehicle.y and self.y - vehicle.y < self.height + SAFE_DISTANCE:
                        # Slow down if the vehicle ahead is too close
                        self.speed = max(0, vehicle.speed * 0.75)  # Reduce speed, but not to zero
                        break
            # Move the vehicle if there is enough space
            self.y -= self.speed

            if self.y <= 0:
                self.has_crossed_junction = False  # Wrap around to the start
        
        if self.has_crossed:
            vehicles.remove(self)

    def follow_queue(self, vehicles, signal):
        """Ensure the vehicle follows the car in front of it"""
        for vehicle in vehicles:
            if signal == RED:  # Only check if the light is red
                if vehicle != self and vehicle.direction == self.direction:
                    # Check if the vehicle is in front and in the same lane
                    if self.direction in ["right", "left"] and abs(self.x - vehicle.x) < self.width + 10:
                        # If in the same lane and close, stop and wait for the car in front to move
                        self.speed = max(0, vehicle.speed * 0.75)  # Adjust speed to follow the vehicle
                    elif self.direction in ["up", "down"] and abs(self.y - vehicle.y) < self.height + 10:
                        # Same lane, close enough to stop
                        self.speed = max(0, vehicle.speed * 0.75)  # Adjust speed to follow the vehicle
                    break  # No need to check other vehicles once we've adjusted position
            self.speed = 2  # Reset speed once we've checked the queue

    def draw(self, screen):
        """Draw the vehicle on the screen"""
        screen.blit(self.image, (self.x, self.y))
        
        

        # Display the battery percentage for EV vehicles
        if self.vehicle_type == "EV":
            font = pygame.font.Font(None, 19)
            battery_text = f"{int(self.battery)}%"
            battery_surface = font.render(battery_text, True, (0, 0, 0))
            
            if self.direction in ["up"]:
                screen.blit(battery_surface, (self.x +12, self.y +  self.height -13))

            elif self.direction in ["down"]:
                screen.blit(battery_surface, (self.x + 22, self.y ))
            
            elif self.direction in ["right"]:
                rotated_battery_surface = pygame.transform.rotate(battery_surface, 90)
                text_rect = rotated_battery_surface.get_rect(center=(self.x + 7, (self.y +17)))
                screen.blit(rotated_battery_surface,text_rect)
            
            elif self.direction in ["left"]:
                rotated_battery_surface = pygame.transform.rotate(battery_surface, 90)
                text_rect = rotated_battery_surface.get_rect(center=(self.x + 45, (self.y + self.height // 2)+4))
                screen.blit(rotated_battery_surface,text_rect)

def spawn_new_vehicles(vehicles,index):
    """Periodically spawn new vehicles, but regulate spawn rate"""
    if len(vehicles) < MAX_VEHICLES:  # Only spawn if the vehicle count is less than MAX_VEHICLES
        new_vehicles = []

        # Define a function to check if a new vehicle's spawn position overlaps with an existing vehicle
        def is_position_free(x, y, direction):
            for vehicle in vehicles:
                # Check for overlap based on direction
                if direction == "right" and vehicle.direction == "right" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                    return False
                if direction == "left" and vehicle.direction == "left" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                    return False
                if direction == "down" and vehicle.direction == "down" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                    return False
                if direction == "up" and vehicle.direction == "up" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                    return False
            return True

        # Attempt to spawn vehicles
        for _ in range(1):
            # Spawn right-moving vehicles
            global i
            vehicle_type = random.choices(["Emergency", "EV", "AV", "Normal"], weights = [1, 3, 2, 3])[0]
            direction = random.choice(["right","left","up","down"])

            if direction == "right":
                while True:
                    x = random.randint(0, 200) if index==0 else random.randint(0,80) 
                    y = random.choice(LANE_POSITIONS["right"])
                    if is_position_free(x, y, "right"):
                        new_vehicles.append(Vehicle(x, y, vehicle_type, "right", index))
                        break

            # Spawn down-moving vehicles
            if direction == "down":
                while True:
                    x = random.choice(LANE_POSITIONS["down"])
                    y = random.randint(0, 200) if index==0 else random.randint(0,80)
                    if is_position_free(x, y, "down"):
                        new_vehicles.append(Vehicle(x, y, vehicle_type, "down", index))
                        break

            # Spawn left-moving vehicles
            if direction == "left":
                while True:
                    x = random.randint( 0 , 200) if index==0 else random.randint(0,80)
                    y = random.choice(LANE_POSITIONS["left"])
                    if is_position_free(x, y, "left"):
                        new_vehicles.append(Vehicle(x, y, vehicle_type, "left", index))
                        break

            # Spawn up-moving vehicles
            if direction == "up":
                while True:
                    x = random.choice(LANE_POSITIONS["up"])
                    y = random.randint(0, 200) if index==0 else random.randint(0,80)
                    if is_position_free(x, y, "up"):
                        new_vehicles.append(Vehicle(x, y, vehicle_type, "up", index))
                        break
            index+=len(new_vehicles)

        return new_vehicles , index

    return [] , index# No vehicles spawned if we hit the max limit



def emergency_priority(vehicles,index):

    new_vehicles = []

    # Define a function to check if a new vehicle's spawn position overlaps with an existing vehicle
    def is_position_free(x, y, direction):
        for vehicle in vehicles:
            # Check for overlap based on direction
            if direction == "right" and vehicle.direction == "right" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                return False
            if direction == "left" and vehicle.direction == "left" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                return False
            if direction == "down" and vehicle.direction == "down" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                 return False
            if direction == "up" and vehicle.direction == "up" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                return False
        return True

    for i in range(6):

        if i==1:
            vehicle_type = "Emergency"
            x = random.randint(0, 200) if index==0 else random.randint(0,80) 
            y = random.choice(LANE_POSITIONS["right"])
            if is_position_free(x, y, "right"):
                new_vehicles.append(Vehicle(x, y, vehicle_type, "right", index))
                
            
                        
        else :
            vehicle_type = random.choice(["EV","AV","Normal"])
            x = random.choice(LANE_POSITIONS["up"])
            y = random.randint(0, 200) if index==0 else random.randint(0,80)
            if is_position_free(x, y, "up"):
                new_vehicles.append(Vehicle(x, y, vehicle_type, "up", index))
            
                    
            
            
    return new_vehicles , index

def ev_charge(vehicles,index):

    new_vehicles = []

    # Define a function to check if a new vehicle's spawn position overlaps with an existing vehicle
    def is_position_free(x, y, direction):
        for vehicle in vehicles:
            # Check for overlap based on direction
            if direction == "right" and vehicle.direction == "right" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                return False
            if direction == "left" and vehicle.direction == "left" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                return False
            if direction == "down" and vehicle.direction == "down" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                 return False
            if direction == "up" and vehicle.direction == "up" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                return False
        return True

    for i in range(6):

        if i in [ 1,2,3]:
            vehicle_type = "EV"
            x = random.choice(LANE_POSITIONS["up"])
            y = random.randint(0, 200) if index==0 else random.randint(0,80)
            if is_position_free(x, y, "up"):
                new_vehicles.append(Vehicle(x, y, vehicle_type, "up", index))
                
        else :
            vehicle_type = random.choice(["AV", "Normal"])
            x = random.randint(0, 200) if index==0 else random.randint(0,80) 
            y = random.choice(LANE_POSITIONS["right"])
            if is_position_free(x, y, "right"):
                new_vehicles.append(Vehicle(x, y, vehicle_type, "right", index))
            
    return new_vehicles , index

def long_line(vehicles,index):

    new_vehicles = []

    # Define a function to check if a new vehicle's spawn position overlaps with an existing vehicle
    def is_position_free(x, y, direction):
        for vehicle in vehicles:
            # Check for overlap based on direction
            if direction == "right" and vehicle.direction == "right" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                return False
            if direction == "left" and vehicle.direction == "left" and abs(vehicle.y - y) < 20 and abs(vehicle.x - x) < 40:
                return False
            if direction == "down" and vehicle.direction == "down" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                 return False
            if direction == "up" and vehicle.direction == "up" and abs(vehicle.x - x) < 20 and abs(vehicle.y - y) < 40:
                return False
        return True

    for i in range(9):

        if i in [1 , 2 ,3]:
            vehicle_type = random.choice(["EV","AV","Normal"])
            x = random.randint(0, 200) if index==0 else random.randint(0,80) 
            y = random.choice(LANE_POSITIONS["right"])
            if is_position_free(x, y, "right"):
                new_vehicles.append(Vehicle(x, y, vehicle_type, "right", index))
            
                        
        else :
            vehicle_type =  random.choice(["Normal","EV"])
            x = random.choice(LANE_POSITIONS["up"])
            y = random.randint(0, 200) if index==0 else random.randint(0,80)
            if is_position_free(x, y, "up"):
                new_vehicles.append(Vehicle(x, y, vehicle_type, "up", index))
            
            
    return new_vehicles , index

                        


e_priority = 0
w_priority = 0
n_priority = 0
s_priority = 0

def optimize_traffic_flow(vehicles):
    """Adjust traffic signals based on the number of EVs and AVs in each direction."""
    global signal_states, signal_timer ,n_priority, s_priority, e_priority, w_priority

    # Count priority vehicles in each direction
    

    for v in vehicles:
        if v.direction == "right" and v.x <= 360 :
            e_priority += v.priority
            
        elif v.direction == "left" and v.x >= 580 :
            w_priority += v.priority
            
        elif v.direction == "down" and v.y <= 240 :
            s_priority += v.priority
            

        elif v.direction == "up" and v.y >= 460 :
            n_priority += v.priority
            

        # Change signals if one direction has significantly more priority vehicles
        if n_priority >= max(s_priority, e_priority, w_priority)  and time.time() - signal_timer > signal_duration:  # Threshold for switching
            signal_states["North"], signal_states["Soth"] , signal_states["East"], signal_states["West"]= GREEN, RED, RED, RED
            change = True
            signal_timer = time.time()  # Reset the timer

            # Reset queue positions for all vehicles
            for vehicle in vehicles:
                vehicle.queue_position = None

        elif s_priority >= max(n_priority, e_priority, w_priority)  and time.time() - signal_timer > signal_duration:

            signal_states["North"], signal_states["South"], signal_states["East"], signal_states["West"] = RED, GREEN, RED, RED
            change = True
            signal_timer = time.time()  # Reset the timer

            # Reset queue positions for all vehicles
            for vehicle in vehicles:
                vehicle.queue_position = None
    
        elif e_priority >= max(s_priority, n_priority, w_priority)  and time.time() - signal_timer > signal_duration:
            signal_states["North"], signal_states["South"], signal_states["East"], signal_states["West"] = RED, RED, GREEN, RED
            change = True
            signal_timer = time.time()  # Reset the timer

            # Reset queue positions for all vehicles
            for vehicle in vehicles:
                vehicle.queue_position = None
    
        elif w_priority >= max(s_priority, e_priority, n_priority)  and time.time() - signal_timer > signal_duration:
            signal_states["North"], signal_states["South"], signal_states["East"], signal_states["West"] = RED, RED, RED, GREEN
            change = True
            signal_timer = time.time()  # Reset the timer

            # Reset queue positions for all vehicles
            for vehicle in vehicles:
                vehicle.queue_position = None

    for vehicle in vehicles:

        if vehicle.direction == "right" and vehicle.has_crossed_junction:
            e_priority-=vehicle.priority
            
        elif vehicle.direction == "left" and vehicle.has_crossed_junction:
            w_priority-=vehicle.priority
        
        elif vehicle.direction == "down" and vehicle.has_crossed_junction:
            s_priority-=vehicle.priority
            
        elif vehicle.direction == "up" and vehicle.has_crossed_junction:
            n_priority-=vehicle.priority
            

# Initialize vehicles
vehicles = []

# Font for countdown timer
font = pygame.font.Font(None, 36)

# Periodically spawn new vehicles but regulate the number
if scenerio == 1:
    new_vehicles, index = emergency_priority(vehicles, index)
    vehicles.extend(new_vehicles)

elif scenerio == 2:
    new_vehicles, index = ev_charge(vehicles, index)
    vehicles.extend(new_vehicles)

elif scenerio == 3:
    new_vehicles, index = long_line(vehicles, index)
    vehicles.extend(new_vehicles)

elif scenerio == 0:
    new_vehicles, index = spawn_new_vehicles(vehicles, index)
    vehicles.extend(new_vehicles)


# Game loop
running = True
while running:
    i=0
    screen.blit(background_image, (0, 0))  # Draw the background image
    change = False
    

    # Draw extended roads
    pygame.draw.rect(screen, GRAY, (0, 260, WIDTH, 200))
    pygame.draw.rect(screen, GRAY, (380, 0, 200, HEIGHT))
    pygame.draw.rect(screen, WHITE, (0, 360, 380, 5))
    pygame.draw.rect(screen, WHITE, (580, 360, WIDTH, 5))
    pygame.draw.rect(screen, WHITE, (480, 0, 5, 250))
    pygame.draw.rect(screen, WHITE, (480, 460, 5, HEIGHT))
    # Draw traffic light boxes
    pygame.draw.rect(screen, BLACK, (300, 160, 50, 80))  # North-South Light Box (Top)
    pygame.draw.rect(screen, BLACK, (300, 480, 50, 80))  # South-North Light Box (Bottom)
    pygame.draw.rect(screen, BLACK, (615, 160, 50, 80))  # East-West Light Box (Left)
    pygame.draw.rect(screen, BLACK, (615, 480, 50, 80))  # West-East Light Box (Right))

    # Draw traffic lights
    for i, (direction, color) in enumerate(signal_states.items()):
        # North-South lights
        x , y, a, b = 0, 0, 0, 00
        
        if direction == "North":
            x, y = (325, 500) 
            light_color = GREEN if color == GREEN else RED
            pygame.draw.circle(screen, light_color, (x, y), 15)
            pygame.draw.circle(screen, YELLOW if (time.time() - signal_timer > signal_duration -1) and (change == True) else GRAY, (x, y + 40), 15) 
            change = False
        elif direction == "East":
            x, y = (325, 180)
            light_color = GREEN if color == GREEN else RED
            pygame.draw.circle(screen, light_color, (x, y), 15)
            pygame.draw.circle(screen, YELLOW if (time.time() - signal_timer > signal_duration -1) and (change == True) else GRAY, (x, y + 40), 15)
            change = False
        elif direction == "South":
            a, b = (640, 180) 
            light_color = GREEN if color == GREEN else RED
            pygame.draw.circle(screen, light_color, (a, b), 15)
            pygame.draw.circle(screen, YELLOW if (time.time() - signal_timer > signal_duration -1) and (change == True) else GRAY, (a, b + 40), 15)
            change = False
        elif direction == "West" :
            a, b = (640, 500)
            light_color = GREEN if color == GREEN else RED
            pygame.draw.circle(screen, light_color, (a, b), 15)
            pygame.draw.circle(screen, YELLOW if (time.time() - signal_timer > signal_duration - 1) and (change == True) else GRAY, (a, b + 40), 15)
            change = False
        
        

    # Change traffic signals every few seconds
    optimize_traffic_flow(vehicles)

    

    # Move and draw vehicles
    for vehicle in vehicles:
        vehicle.move(vehicles)
        vehicle.draw(screen)
        # Remove vehicles that have crossed the screen
        
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:  # Detect key press
            if event.key == pygame.K_KP1:
                scenerio == 1
            elif event.key == pygame.K_KP2:
                scenerio == 2
            elif event.key == pygame.K_KP3:
                scenerio == 3
                
        if event.type == pygame.QUIT:
            running = False

        

    pygame.display.update()
    pygame.time.delay(30)

pygame.quit()
3