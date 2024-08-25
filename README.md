# Equigence

![Screenshot from 2024-08-24 21-59-23](https://github.com/user-attachments/assets/a32eec77-7707-494b-ba24-9f7405ed1ca9)


A portfolio project that leverages automation to simplify and streamline the analysis of equities, helping long-term investors make data-driven decisions with confidence.

## Getting Started



##### 1. Clone the repository:

``` git clone https://github.com/hlb-git/equigence.git ```

```cd equigence ```

#### 2. Run the dependencies script to install necessary packages:

``` chmod +x dependencies.sh ```     // to change file permission

``` ./dependencies.sh ```
    

#### 3. Initialize Gunicorn:
```
gunicorn -b 0.0.0.0:5000 run:app
```

## Features

#### User Registration and Authentication:
Users can register and log in to access personalized features.

#### Financial Data Retrieval: 
Automatically fetches and processes financial data for various stocks.

#### Data Visualization: 
Provides visual comparisons of key financial metrics over specified periods.

#### User Dashboard: 
Personalized dashboard for users to manage their stock analyses and comparisons.

## Routes Overview

#### Home Page: 
Accessible at ``` / ``` or ``` /home ```, renders the landing page.

#### Register Page: 
Accessible at ```/register```, allows new users to register. Redirects authenticated users to the dashboard.

## Contributing

* Fork the repository.
* Create a new branch ```git checkout -b feature-branch```.
* Make your changes.
* Commit your changes ```git commit -m 'Add some feature'```.
* Push to the branch ```git push origin feature-branch```.
* Open a pull request.
  

## Contact

For any inquiries or issues, please contact mzeelovegeneral@gmail.com
