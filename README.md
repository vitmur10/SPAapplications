# SPA application: Comments.

The Comment Management project is a web application developed using the Django framework and the Vue.js frontend library. It provides the ability to add and manage comments on a web page. In this README you will find information on how to install, configure and use this application.
## Requirements

To successfully deploy and run the project, you will need the following dependencies listed in the `requirements.txt` file:

- Django 4.2.6
- Django REST framework 3.14.0
- And other dependencies that will be installed automatically when setting up the environment.

## Installation

1. Clone the project repository to your local computer:

    ```bash
    git clone https://github.com/Dogherty/SPA-application-Comments.git

2. Create and activate the virtual environment for the project:

    ```bash
    python -m venv myenv
    source myenv/bin/activate

3. Install the Python dependencies specified in requirements.txt:

    ```bash
    pip install -r requirements.txt
   
4. Go to the project directory:

    ```bash
    cd your_project_directory


6. Apply database migration:

    ```bash
    python manage.py migrate

7. Start the Django development server:

    ```bash
    python manage.py runserver

## Preparation for work

1. Create a superuser:

    ```bash
    python manage.py createsuperuser

2. Go to the administrative panel at the address http://127.0.0.1/admin/ and log in using superuser credentials.


Done! Now you can move on to testing the comments system.

## Usage

The application provides the following functions:

- Adding comments: Users can add new comments by specifying their name, email address, website, comment text, and uploading images or text files.

- Reply to comments: Users can leave replies to existing comments.

- Pagination: Comments are divided into pages for ease of navigation. By default - 25 comments per page.

- Captcha: Captcha is provided for security of access to adding comments.

- Uploading images and files: Users can upload images and text files to their comments.
    > The image must be no more than 320x240 pixels, if requested it will be filled
the image is larger, the image is proportional
decreases to the given size. Acceptable file formats: JPG, GIF, PNG.

    > The text file must be no more than 100 Kb. Acceptable file formats: TXT.
