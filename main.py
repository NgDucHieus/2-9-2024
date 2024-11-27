import turtle

def draw_star(x, y, size, color):
    turtle.penup()
    turtle.goto(x, y - size / 2)  # Position the star to be centered
    turtle.pendown()
    turtle.color(color)
    turtle.begin_fill()
    for _ in range(5):
        turtle.forward(size)
        turtle.right(144)
    turtle.end_fill()

def draw_vietnam_flag():
    turtle.speed(5)
    
    # Draw red rectangle
    turtle.penup()
    turtle.goto(-200, 150)  # Top-left corner of the rectangle
    turtle.pendown()
    turtle.color("red")
    turtle.begin_fill()
    for _ in range(2):
        turtle.forward(400)  # Width of the flag
        turtle.right(90)
        turtle.forward(300)  # Height of the flag
        turtle.right(90)
    turtle.end_fill()
    
    # Draw yellow star at the center of the flag
    draw_star(-70, 100, 150, "yellow")
    
    turtle.hideturtle()
    turtle.done()

draw_vietnam_flag()
