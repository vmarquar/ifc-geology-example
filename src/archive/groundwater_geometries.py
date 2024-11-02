import math
import matplotlib.pyplot as plt
import ezdxf
from ezdxf.render.forms import rotation_form
from typing import Iterable

def calculate_R(s, k):
    """
    Calculate R based on the Sichardt formula.

    Parameters:
    s (float): Absenkung in m
    k (float): kf-Wert
    
    Returns:
    float: The calculated value of R
    """
    return 3000 * s * math.sqrt(k)

def calculate_y(h, Q, k, r, x, s, H):
    """
    Calculate y based on the given formula, with additional constraints.

    Parameters:
    h (float): Wassererfüllte Restmächtigkeit in m (Wassererfüllte Mächtigkeit des Aquifers vor der Absenkung minus Absenkung)
    Q (float): Pumprate in m3/s
    k (float): kf-Wert
    r (float): Brunnenradius in m
    x (float): Entfernung von der Brunnenachse in m
    s (float): Absenkung in m
    H (float): Wassererfüllte Mächtigkeit des Aquifers vor der Absenkung in m (y value when x >= R)
    
    Returns:
    float: The calculated value of y or H if x >= R
    """
    R = calculate_R(s, k)
    
    if x >= R:
        return H
    
    if x <= r:
        return h
    
    term = (Q / (math.pi * k)) * math.log(r / x)
    y = math.sqrt(h**2 - term)
    return y

def generate_x_values(start, end, num_points):
    """
    Generate a list of x values from start to end with num_points points.

    Parameters:
    start (float): The starting value of x
    end (float): The ending value of x
    num_points (int): The number of points to generate
    
    Returns:
    list: A list of x values
    """
    return [start + i * (end - start) / (num_points - 1) for i in range(num_points)]


def plot_result(x_values,y_values, equal_axis=True):
    plt.figure(figsize=(10, 6))
    plt.plot(x_values, y_values, label='y vs x')
    plt.axvline(x=R, color='red', linestyle='--', label='R')
    plt.xlabel('Entfernung von der Brunnenachse (x in m)')
    plt.ylabel('y')
    plt.title('Graph of y vs x')
    plt.legend()
    plt.grid(True)
    if(equal_axis):
        plt.axis('equal')  # Set equal aspect ratio for x and y axes
    plt.show()


# add main 
if __name__ == "__main__":
        
    # Example usage and plotting:
    r = 0.20  # Brunnenradius in m
    Q = 0.043  # Pumprate in m3/s
    k = 3.09e-03  # kf-Wert
    s = 1.32  # Absenkung in m
    H = 15.0  # Wassererfüllte Mächtigkeit des Aquifers vor der Absenkung in m
    h = H - s  # Wassererfüllte Restmächtigkeit in m

    # Calculate R
    R = calculate_R(s, k)

    # Generate x values from 0.1 to R
    x_values = generate_x_values(0.0, R, 500)  # Using 0.1 to avoid log(0) issue
    #x_values = generate_x_values(0.0, 10, 500)  # Using 0.1 to avoid log(0) issue
    y_values = [calculate_y(h, Q, k, r, x, s, H) for x in x_values]

    # Plot the results
    #plot_result(x_values,y_values, equal_axis=False)
    plot_result(x_values,y_values)

    # Generate profile for rotation
    profile = [(x, y-h) for x, y in zip(x_values, y_values)]
    y_values_offset = [y-h for y in y_values]
    plot_result(x_values, y_values_offset)
    # Create a rotation form using the profile
    mesh = rotation_form(count=10, profile=profile, axis=(0,1,0))
    mesh.rotate_y(angle=math.radians(35))

    # Save the rotation form as a DXF file
    doc = ezdxf.new()
    msp = doc.modelspace()
    mesh.render_mesh(msp)
    folder = "/Users/valentin/Desktop/Share/01-5_dxfs/"
    doc.saveas(folder+"rotation_form.dxf")

    print("DXF file 'rotation_form.dxf' created successfully.")
