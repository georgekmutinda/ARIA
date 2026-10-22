import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay
class Visualizer:
    @staticmethod
    def plot_confusion_matrix(cm, class_names):
        fig, ax = plt.subplots(figsize=(10, 10))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
        disp.plot(cmap=plt.cm.Blues, xticks_rotation=45, ax=ax)
        plt.title("Confusion Matrix")
        plt.tight_layout()
        plt.show()