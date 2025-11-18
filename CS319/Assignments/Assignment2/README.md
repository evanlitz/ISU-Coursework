# SkillFlix

## Project Overview


This project meets all of the assigned requirements for the SkillFlix Assignment 2 of the CS319 curriculum. This application follows the format of many online course websites and displays courses and their associated information, along with providing a system for users to explore courses, sign up for courses, and enter their information and pay for courses. It is inspired by Netflix-style platform design (frontend). It was collabroately completed through Gitlabs by Evan Litzer and Lindsay Ngobo Ndjele

## Purpose

The goal of this assignment is to apply our learning of technologies like Tailwind and React components and channel it into a group-project application. Implementing these technologies together can help us learn important skills that can be useful for our career. We chose cooking as our topic for the project, as it is also the theme of our midterm and final project. One thing that we believe we grasped the most from this assignment is how pages work together and pass information/parameters when needed. This transforms our previous web development into full stack apps that users can logically follow and avoid reinputting the same information. 

Core react components were applied, including useState and useEffect functions for each page. Also, useNavigate hooked pages together and helped pass data from one page to another. Also, tailwind css styling was first introduced with this project, including local and global classes. These topics that we learned were also stacked upon what has been taught previously in this course regarding web design principles. Our expertise will only continue to grow with more class projects.

## Features

- List and briefly describe each major view:
 - Browse Courses (Home.Jsx) page:
This page showcases the three categories of cooking courses availble in the project. It includes a brief description of the course, the course image, and the author. The three categories are split, and users can click the "More Details" button to navigate to the course details page for the selected course.
 - Course Details:
This view dynamically displays detailed information for the selected course.
When a user clicks “View Details” from the Browse Courses page, the application navigates to this route and passes the selected course object through React Router state.
 -Enrollment Form Page:
This page contains the logic for a user to sign up for a course. It requires them to insert information into the entry fields in order to sign up for the course. It includes course start date, online or in person option, email, message to instructor, and name. There is also validation methods that ensure that these fields are filled to then sign up for the course.
  - Payment & Confirmation:
This view finalizes the enrollment process. It receives the course and form data from the Enrollment Form View and generates a full checkout interface.

## Setup Instructions

- git clone https://git.las.iastate.edu/se-coms-3190/fall-2025/assignment-2/PS_19.git
- cd PS_19
- npm install
- npm run dev

## Team Members & Roles

- Member 1: Evan Litzer
  - Browse Courses page (home.jsx)
  - Enrollment page (EnrollmentForm.jsx)
  - Data Json file and uploading videos
  - Main.Jsx
- Member 2: Lindsay Ngobo Ndjele
  - Navbar.jsx
  - PaymentConfirmation.jsx 
  - CourseDetails.jsx
  - Index.css file
  - Color styling

## Design Summary

The project uses Tailwind CSS for rapid, utility-based styling and consistent responsive behavior.
Each view uses semantic color accents and rounded containers to improve visual hierarchy.
The grid layouts in both Course Details and Payment & Confirmation ensure components scale smoothly between mobile and desktop screens.
The Navbar provides intuitive navigation with clear hover feedback, and index.css defines base colors and global styling shared across components.

## Demo
https://iowastate-my.sharepoint.com/:v:/r/personal/nnwlinds_iastate_edu/Documents/Assignment2Demo.mp4?csf=1&web=1&e=Xf85pa&nav=eyJyZWZlcnJhbEluZm8iOnsicmVmZXJyYWxBcHAiOiJTdHJlYW1XZWJBcHAiLCJyZWZlcnJhbFZpZXciOiJTaGFyZURpYWxvZy1MaW5rIiwicmVmZXJyYWxBcHBQbGF0Zm9ybSI6IldlYiIsInJlZmVycmFsTW9kZSI6InZpZXcifX0%3D


## Notes

