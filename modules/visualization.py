import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Slider

# Constants for annotation and visualization
K0_ANNOTATION_OFFSET = (0, 10)
SUBSTANCE_ANNOTATION_OFFSET = (0, 25)
K0_MATCH_TOLERANCE = 0.02
PEAK_MARKER_SIZE = 50

def create_spectrum_plot(spectrums, peaks_data, identified_substances=None):
    """
    Create a plot showing spectra with peaks and identified substances.
    
    Parameters:
    - spectrums: dictionary with 'pos' and 'neg' arrays
    - peaks_data: dictionary with 'pos' and 'neg' peak information (index, height)
    - identified_substances: list of identified substances with their K0 matches
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Plot positive spectrum
    if 'pos' in spectrums and spectrums['pos'] is not None and len(spectrums['pos']) > 0:
        ax1.plot(spectrums['pos'], color='blue', label='Positive Spectrum')
        
        if 'pos' in peaks_data and peaks_data['pos']:
            peak_indices = [p[0] for p in peaks_data['pos']]
            peak_heights = [p[1] for p in peaks_data['pos']]
            ax1.scatter(peak_indices, peak_heights, color='red', s=PEAK_MARKER_SIZE, marker='x', label='Peaks')
            
            # Annotate peaks with K0 values
            for i, (idx, height) in enumerate(zip(peak_indices, peak_heights)):
                ax1.annotate(f"K0: {peaks_data['pos_k0s'][i]:.3f}", 
                            (idx, height),
                            textcoords="offset points", 
                            xytext=K0_ANNOTATION_OFFSET,
                            ha='center')
                
                # Mark identified substances
                if identified_substances:
                    for substance in identified_substances:
                        for match in substance['pos_matches']:
                            if abs(peaks_data['pos_k0s'][i] - match[2]) <= K0_MATCH_TOLERANCE:
                                ax1.annotate(f"{substance['name']}", 
                                           (idx, height),
                                           textcoords="offset points", 
                                           xytext=SUBSTANCE_ANNOTATION_OFFSET,
                                           ha='center', 
                                           color='green',
                                           weight='bold')
    
    # Plot negative spectrum
    if 'neg' in spectrums and spectrums['neg'] is not None and len(spectrums['neg']) > 0:
        ax2.plot(spectrums['neg'], color='green', label='Negative Spectrum')
        
        if 'neg' in peaks_data and peaks_data['neg']:
            peak_indices = [p[0] for p in peaks_data['neg']]
            peak_heights = [p[1] for p in peaks_data['neg']]
            ax2.scatter(peak_indices, peak_heights, color='red', s=PEAK_MARKER_SIZE, marker='x', label='Peaks')
            
            # Annotate peaks with K0 values
            for i, (idx, height) in enumerate(zip(peak_indices, peak_heights)):
                ax2.annotate(f"K0: {peaks_data['neg_k0s'][i]:.3f}", 
                            (idx, height),
                            textcoords="offset points", 
                            xytext=K0_ANNOTATION_OFFSET,
                            ha='center')
                
                # Mark identified substances
                if identified_substances:
                    for substance in identified_substances:
                        for match in substance['neg_matches']:
                            if abs(peaks_data['neg_k0s'][i] - match[2]) <= K0_MATCH_TOLERANCE:
                                ax2.annotate(f"{substance['name']}", 
                                           (idx, height),
                                           textcoords="offset points", 
                                           xytext=SUBSTANCE_ANNOTATION_OFFSET,
                                           ha='center', 
                                           color='green',
                                           weight='bold')
    
    ax1.set_title('Positive Spectrum')
    ax1.set_xlabel('Index')
    ax1.set_ylabel('Intensity')
    ax1.legend()
    ax1.grid(True)
    
    ax2.set_title('Negative Spectrum')
    ax2.set_xlabel('Index')
    ax2.set_ylabel('Intensity')
    ax2.legend()
    ax2.grid(True)
    
    plt.tight_layout()
    return fig

def show_scrollable_plots(data_list):
    """
    Create a scrollable interface to navigate through multiple spectrum plots.
    
    Parameters:
    - data_list: List of dictionaries containing spectrum data for each measurement
    """
    if not data_list:
        print("No data to display")
        return
    
    # Create a figure that will persist
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    # Slider position adjustment
    SLIDER_BOTTOM_MARGIN = 0.15
    plt.subplots_adjust(bottom=SLIDER_BOTTOM_MARGIN)
    
    # Function to update the plot
    def update_plot(idx):
        ax1.clear()
        ax2.clear()
        
        current_data = data_list[idx]
        
        # Plot positive spectrum
        if current_data['spectrums']['pos'] is not None:
            pos_spectrum = current_data['spectrums']['pos']
            ax1.plot(pos_spectrum, color='blue', label='Positive Spectrum')
            
            if current_data['peaks_data']['pos']:
                peak_indices = [p[0] for p in current_data['peaks_data']['pos']]
                peak_heights = [p[1] for p in current_data['peaks_data']['pos']]
                ax1.scatter(peak_indices, peak_heights, color='red', s=PEAK_MARKER_SIZE, marker='x', label='Peaks')
                
                # Annotate peaks with K0 values
                for i, (idx, height) in enumerate(zip(peak_indices, peak_heights)):
                    ax1.annotate(f"K0: {current_data['peaks_data']['pos_k0s'][i]:.3f}", 
                                (idx, height),
                                textcoords="offset points", 
                                xytext=K0_ANNOTATION_OFFSET,
                                ha='center')
                    
                    # Mark identified substances
                    if current_data['identified_substances']:
                        for substance in current_data['identified_substances']:
                            for match in substance['pos_matches']:
                                if abs(current_data['peaks_data']['pos_k0s'][i] - match[2]) <= K0_MATCH_TOLERANCE:
                                    ax1.annotate(f"{substance['name']}", 
                                               (idx, height),
                                               textcoords="offset points", 
                                               xytext=SUBSTANCE_ANNOTATION_OFFSET,
                                               ha='center', 
                                               color='green',
                                               weight='bold')
        
        # Plot negative spectrum
        if current_data['spectrums']['neg'] is not None:
            neg_spectrum = current_data['spectrums']['neg']
            ax2.plot(neg_spectrum, color='green', label='Negative Spectrum')
            
            if current_data['peaks_data']['neg']:
                peak_indices = [p[0] for p in current_data['peaks_data']['neg']]
                peak_heights = [p[1] for p in current_data['peaks_data']['neg']]
                ax2.scatter(peak_indices, peak_heights, color='red', s=PEAK_MARKER_SIZE, marker='x', label='Peaks')
                
                # Annotate peaks with K0 values
                for i, (idx, height) in enumerate(zip(peak_indices, peak_heights)):
                    ax2.annotate(f"K0: {current_data['peaks_data']['neg_k0s'][i]:.3f}", 
                                (idx, height),
                                textcoords="offset points", 
                                xytext=K0_ANNOTATION_OFFSET,
                                ha='center')
                    
                    # Mark identified substances
                    if current_data['identified_substances']:
                        for substance in current_data['identified_substances']:
                            for match in substance['neg_matches']:
                                if abs(current_data['peaks_data']['neg_k0s'][i] - match[2]) <= K0_MATCH_TOLERANCE:
                                    ax2.annotate(f"{substance['name']}", 
                                               (idx, height),
                                               textcoords="offset points", 
                                               xytext=SUBSTANCE_ANNOTATION_OFFSET,
                                               ha='center', 
                                               color='green',
                                               weight='bold')
        
        ax1.set_title('Positive Spectrum')
        ax1.set_xlabel('Index')
        ax1.set_ylabel('Intensity')
        ax1.legend()
        ax1.grid(True)
        
        ax2.set_title('Negative Spectrum')
        ax2.set_xlabel('Index')
        ax2.set_ylabel('Intensity')
        ax2.legend()
        ax2.grid(True)
        
        fig.suptitle(f"Measurement Time: {current_data['measurement_time']}", fontsize=16)
        fig.canvas.draw_idle()
    
    # Initial plot
    update_plot(0)
    
    # Add slider
    SLIDER_X_POSITION = 0.25
    SLIDER_Y_POSITION = 0.05
    SLIDER_WIDTH = 0.65
    SLIDER_HEIGHT = 0.03
    ax_slider = plt.axes([SLIDER_X_POSITION, SLIDER_Y_POSITION, SLIDER_WIDTH, SLIDER_HEIGHT])
    slider = Slider(
        ax=ax_slider,
        label='Measurement',
        valmin=0,
        valmax=len(data_list) - 1,
        valinit=0,
        valstep=1
    )
    
    # Connect the slider to the update function
    def update(val):
        update_plot(int(slider.val))
    
    slider.on_changed(update)
    plt.show()
