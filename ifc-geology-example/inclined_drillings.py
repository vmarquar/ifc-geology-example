"""
Hilfreiche Links: https://de.wikipedia.org/wiki/Zylinder_(Geometrie)#/media/Datei:Zylinder-abschnitt-bezeichnungen-s.svg

"""

### LIBRARIES AND MODULES
import numpy as np
import matplotlib.pyplot as plt
from typing_extensions import List, Tuple
import math


### FUNCTION
def get_beta_from_dip(dip:float, zeta:float = 90.0) -> float:
    """
    Diese Funktion gibt den Winkel beta unter Berücksichtung der Verschneidung mit einer Ebene zurück.
    Winkeldefinition siehe: https://de.wikipedia.org/wiki/Zylinder_(Geometrie)#/media/Datei:Zylinder-abschnitt-bezeichnungen-s.svg
    Formeln: https://de.wikipedia.org/wiki/Zylinder_(Geometrie) | Kapitel: Zylinderabschnitt
    Herleitung: Summe im Dreieck = 180° --> Zeichnungen beachten.

    Input:

    dip = Inklination der Bohrung in Grad,
        gemessen von der Horizontalen nach unten.
        Beispiel: dip = 90° wäre eine senkrechte Bohrung,
        dip = 0° wäre eine horizontale Bohrung

    zeta = Neigung des kollidierenden Objekts.
        Beispiel: zeta = 90° für eine senkrecht stehende Wand,
        die von der Bohrung geschnitten wird.
        zeta = 0° für eine horizontale Bodenplatte,
        die von der Bohrung geschnitten wird.
    """
    #TODO
    pass

def get_beta_from_collision_type_and_dip(dip:float, collision_type:str = "WALL") -> float:
    #TODO: add doc-string
    if collision_type == "WALL":
        beta_deg = dip_drilling_deg
    elif collision_type == "FLOOR": # horizontal liegende Bodenplatte
        beta_deg = 90 + dip_drilling_deg
    return beta_deg

def calc_elipsis_axis_lengths_from_inclined_zylinder(beta_deg:float, r:float) -> Tuple[float, float]:
    #TODO: add doc-string

    # Gegebene Parameter
    # r = 0.40  # Radius des Zylinders in Metern
    # #beta_deg = 18.5  # Neigungswinkel in Grad = entspricht dem dip-Winkel der Bohrung

    beta_rad = np.deg2rad(beta_deg)  # Umrechnung in Radiant

    # Berechnung der Halbachsen
    b = r  # Kleine Halbachse
    a = np.sqrt(r**2 + (r * np.tan(beta_rad))**2)  # Große Halbachse, siehe https://de.wikipedia.org/wiki/Zylinder_(Geometrie)

    return(a, b)

def create_plot_from_a_b(a:float, b:float, r:float) -> None:
    #TODO: add doc-string

    # Ellipse parametrisch darstellen
    t = np.linspace(0, 2*np.pi, 1000)

    x = a * np.cos(t)
    y = b * np.sin(t)
    # Plot erstellen
    plt.figure(figsize=(8, 8))
    plt.plot(x, y, label=f'Ellipse (r={r} m, β={beta_deg}°)')
    plt.axhline(0, color='grey', linewidth=0.5)
    plt.axvline(0, color='grey', linewidth=0.5)

    # Halbachsen in die Grafik einfügen
    plt.plot([0, a], [0, 0], 'r--', label=f'Große Halbachse a = {a:.2f} m')
    plt.plot([0, 0], [0, b], 'b--', label=f'Kleine Halbachse b = {b:.2f} m')

    # Achsen und Titel beschriften
    plt.xlabel('x (m)')
    plt.ylabel('y (m)')
    plt.title('Ellipse als Schnittfigur eines geneigten Zylinders')
    plt.legend()
    plt.axis('equal')
    plt.grid(True)

    # Halbachsen beschriften
    plt.text(a/2, 0.02, f'a = {a:.2f} m', color='red', ha='center')
    plt.text(0.02, b/2, f'b = {b:.2f} m', color='blue', va='center', rotation=90)

    plt.show()

### MAIN
if __name__ == "__main__":

    # 0) Define input parameters:
    dip_drilling_deg = 18.5 # Inklination der Bohrung in Grad, gemessen von der Horizontalen nach unten. Beispiel: dip = 90° wäre eine senkrechte Bohrung, dip = 0° wäre eine horizontale Bohrung
    RADIUS = 0.40 # meter

    point1 = (50,0,60) # y = 0 = const. = 2D-Schnitt entlang y = 0
    point2 = (0,0,50)
    point3 = (0,0,0)
    point4 = (50,0,0)


    # 1) Calculate the angle beta between the collision plane and the cylinder:
    beta_deg = get_beta_from_collision_type_and_dip(dip_drilling_deg, collision_type="WALL")

    # 2) Calculate the minor and mayor axis a and b from the angle beta
    a,b = calc_elipsis_axis_lengths_from_inclined_zylinder(beta_deg, r=RADIUS)

    # 3) Plot the ellipsis
    # create_plot_from_a_b(a, b, radius)

    # 4) berechne den Dip, für den ersten Zielpunkt aus der Winkeltrigonometrie zwischen point1 und point2
    # y = const
    x1 = point1[0]
    x2 = point2[0]
    z1 = point1[2]
    z2 = point2[2]
    seite_a = abs(x2 - x1)
    seite_b = abs(z2 - z1)
    alpha = math.atan(seite_b/seite_a)
    alpha_deg = np.rad2deg(alpha)
    first_dip_deg = alpha_deg

    # 5) Berechne das erste a, und b Pärchen aus dem ersten Dip und der collision_type=WALL
    first_beta_deg = get_beta_from_collision_type_and_dip(first_dip_deg, collision_type="WALL")

    # 2) Calculate the minor and mayor axis a and b from the angle beta
    first_a,first_b = calc_elipsis_axis_lengths_from_inclined_zylinder(first_beta_deg, r=RADIUS)
    print(first_a, first_b)
    second_target_point = z2 - first_a
    # then loop until z3 @ point3 is reached
