from datetime import datetime
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import messagebox


def calculate_weighted_scores(selected_sentiment_data, user_ranking: dict[str, int]):
    """
    Calculates the weighted scores for each selected hotel based on sentiment data and user rankings.

    :param selected_sentiment_data: DataFrame containing sentiment ratios for the selected hotels.
    :param user_ranking: Dictionary with topic scores between 0 and 5.
    :return: DataFrame with selected hotels and their weighted scores.
    """

    # Normalise user rankings to create weights.
    weights = np.array([user_ranking[cat] for cat in user_ranking.keys()])
    normalized_weights = weights / np.sum(weights)

    # Calculate the weighted score using sentiment ratios and user rankings.
    weighted_scores = selected_sentiment_data[list(user_ranking.keys())].mul(normalized_weights)
    selected_sentiment_data['Weighted Score'] = weighted_scores.sum(axis=1)

    return selected_sentiment_data[['Hotel Name', 'Weighted Score']]


# Tkinter GUI
class HotelRecommendationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Recommendation System")

        # Load sentiment data
        self.sentiment_data = pd.read_csv('sentiment_ratio_per_hotel_london.csv')

        # Initialize variables
        self.selected_hotels = []
        self.user_ranking = {}

        # Setup pages
        self.page1()

    def page1(self):
        self.clear_frame()
        tk.Label(self.root, text="Select Hotels").pack()
        self.hotel_listbox = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        for hotel in self.sentiment_data['Hotel Name']:
            self.hotel_listbox.insert(tk.END, hotel)
        self.hotel_listbox.pack()

        tk.Button(self.root, text="Next", command=self.page2).pack()

    def page2(self):
        self.selected_hotels = [self.hotel_listbox.get(i) for i in self.hotel_listbox.curselection()]
        if not self.selected_hotels:
            messagebox.showerror("Input Error", "Please select at least one hotel.")
            return

        self.clear_frame()
        tk.Label(self.root, text="Rank Preferences (0-5)").pack()

        self.room_amenities_var = tk.StringVar()
        tk.Label(self.root, text="Room amenities").pack()
        tk.Entry(self.root, textvariable=self.room_amenities_var).pack()

        self.hotel_amenities_var = tk.StringVar()
        tk.Label(self.root, text="Hotel amenities").pack()
        tk.Entry(self.root, textvariable=self.hotel_amenities_var).pack()

        self.staff_var = tk.StringVar()
        tk.Label(self.root, text="Staff").pack()
        tk.Entry(self.root, textvariable=self.staff_var).pack()

        self.food_var = tk.StringVar()
        tk.Label(self.root, text="Food and beverages").pack()
        tk.Entry(self.root, textvariable=self.food_var).pack()

        self.location_var = tk.StringVar()
        tk.Label(self.root, text="Location").pack()
        tk.Entry(self.root, textvariable=self.location_var).pack()

        tk.Button(self.root, text="Next", command=self.page3).pack()

    def page3(self):
        try:
            self.user_ranking = {
                'Room amenities': int(self.room_amenities_var.get()),
                'Hotel amenities': int(self.hotel_amenities_var.get()),
                'Staff': int(self.staff_var.get()),
                'Food and beverages': int(self.food_var.get()),
                'Location': int(self.location_var.get())
            }

            for category, score in self.user_ranking.items():
                if not 0 <= score <= 5:
                    raise ValueError(f"Rating for {category} must be between 0 and 5.")

            filtered_sentiment_data = self.sentiment_data[self.sentiment_data['Hotel Name'].isin(self.selected_hotels)]
            weighted_hotel_scores = calculate_weighted_scores(filtered_sentiment_data, self.user_ranking)
            ranked_hotels = weighted_hotel_scores.sort_values('Weighted Score', ascending=False).reset_index(drop=True)
            top_3_hotels = ranked_hotels.head(3)

            output_filename = f"hotel_scores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            ranked_hotels.to_csv(output_filename, index=False)

            self.clear_frame()
            tk.Label(self.root, text="Top 3 Recommended Hotels").pack()
            tk.Label(self.root, text=top_3_hotels[['Hotel Name', 'Weighted Score']].to_string(index=False)).pack()
            tk.Label(self.root, text=f"Ranked hotel scores have been saved to {output_filename}.").pack()
        except ValueError as ve:
            messagebox.showerror("Input Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()


root = tk.Tk()
app = HotelRecommendationApp(root)
root.mainloop()
