import matplotlib.patches as mpatches
import matplotlib.pyplot as plt


plt.plot([1, 2, 3], label="test1")
plt.plot([3, 2, 1], label="test2")


ax = plt.gca()

for i in [0.0, 0.5, 1]:
    for j in [0.0, 0.5, 1]:
        plt.legend(bbox_to_anchor=(0.5, j), loc="upper left", borderaxespad=0.0)
        box = ax.get_position()
        print(f"{box.x0},{box.y0},{box.width * 0.5},{box.height * 0.5}")
        ax.set_position(
            [box.x0, box.y0 + box.height * 0.5, box.width, box.height * 0.5]
        )
        filename = f"basic_{i}_{j}".replace(".", "-")
        print(filename)
        plt.savefig(filename)

