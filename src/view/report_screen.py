import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from .configuration_screen import ConfigurationScreen

class ReportScreen(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.menu_frame = tk.Frame(self)
        self.menu_frame.pack(fill="x")
        tk.Button(self.menu_frame, text="Main", command=lambda: controller.show_frame("MainScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Report", command=lambda: controller.show_frame("ReportScreen")).pack(side="left")
        tk.Button(self.menu_frame, text="Config", command=lambda: controller.show_frame("ConfigurationScreen")).pack(side="left")

        self.chart_frame = ttk.Frame(self)
        self.chart_frame.pack(fill='both', expand=True)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(self.list_frame, columns=('Timestamp', 'Vehicle', 'Lane', 'Image', 'License Plate'), show='headings')
        self.tree.heading('Timestamp', text='Timestamp')
        self.tree.heading('Vehicle', text='Vehicle Type')
        self.tree.heading('Lane', text='Lane ID')
        self.tree.heading('Image', text='Image Path')
        self.tree.heading('License Plate', text='License Plate')
        self.tree.pack(fill='both', expand=True)
        self.scrollbar = ttk.Scrollbar(self.list_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscroll=self.scrollbar.set)
        self.scrollbar.pack(side='right', fill='y')

        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(fill='x')
        tk.Label(self.control_frame, text="Start Date (YYYY-MM-DD):").grid(row=0, column=0)
        self.start_date_entry = ttk.Entry(self.control_frame)
        self.start_date_entry.grid(row=0, column=1)
        tk.Label(self.control_frame, text="End Date (YYYY-MM-DD):").grid(row=0, column=2)
        self.end_date_entry = ttk.Entry(self.control_frame)
        self.end_date_entry.grid(row=0, column=3)
        tk.Button(self.control_frame, text="Update", command=self.update_report).grid(row=0, column=4)
        tk.Button(self.control_frame, text="Export", command=self.export_report).grid(row=0, column=5)

        self.update_report()

    def update_report(self):
        try:
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            df = pd.read_csv('violations.csv')
            if start_date and end_date:
                df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]
                # Thêm bộ lọc theo loại phương tiện
            vehicle_type = self.vehicle_filter.get()  # Giả sử có Combobox cho loại phương tiện
            if vehicle_type:
                df = df[df['Vehicle Type'] == vehicle_type]

            self.ax.clear()
            if not df.empty:
                # Biểu đồ tròn cho loại phương tiện
                vehicle_counts = df['Vehicle Type'].value_counts()
                self.ax.pie(vehicle_counts, labels=vehicle_counts.index, autopct='%1.1f%%')
                self.ax.set_title('Violations by Vehicle Type')
            self.canvas.draw()

            self.ax.clear()
            if not df.empty:
                counts = df['Timestamp'].str.split(' ').str[1].str.split(':').str[0].value_counts().sort_index()
                hours = [f"{h}:00" for h in range(24)]
                counts = [counts.get(str(h).zfill(2), 0) for h in range(24)]
                self.ax.bar(hours, counts)
            self.ax.set_xlabel('Hour')
            self.ax.set_ylabel('Number of Violations')
            self.ax.set_title('Violations by Hour')
            self.canvas.draw()

            for i in self.tree.get_children():
                self.tree.delete(i)
            for _, row in df.iterrows():
                self.tree.insert('', 'end', values=(
                    row['Timestamp'],
                    row['Vehicle Type'],
                    row['Lane ID'],
                    row['Image Path'],
                    row['License Plate']
                ))

        except FileNotFoundError:
            self.ax.clear()
            self.ax.set_title('No violations recorded')
            self.canvas.draw()
        except Exception as e:
            print(f"Error updating report: {e}")

    def export_report(self):
        try:
            df = pd.read_csv('violations.csv')
            start_date = self.start_date_entry.get()
            end_date = self.end_date_entry.get()
            if start_date and end_date:
                df = df[(df['Timestamp'] >= start_date) & (df['Timestamp'] <= end_date)]
            df.to_excel('violations_report.xlsx', index=False)
            print("Exported to violations_report.xlsx")
        except FileNotFoundError:
            print("No violations to export")
        except Exception as e:
            print(f"Error exporting report: {e}")