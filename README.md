# Capstone-Project-LHL
## Real Estate Prediction and Recommendation System

# Purpose

This repository contain codes for extracting, exploring, modelling and presenting an idea of an application to help Real Estate broker better predict and recommend listings for their customer.

This is my final Capstone Project done during the Lighthouse Bootcamp for Data Analyst.

# Inspiration

![The PAIN](/output/figures/the_pain.png)

> "Imagine you're a real estate investor, bombarded with countless property listings. You're overwhelmed, uncertain, and rapidly stuck in 'analysis paralysis'. Meanwhile, real estate brokers, pressed for time, often can't input every property detail accurately. But they excel at painting a vivid picture with words. My project bridges this gap! I've crafted a system where brokers describe a property with their expertise, and investors share their desires in words. Using this, I devised a recommendation system that swiftly identifies the top properties for the investor, cutting through the noise. Now, brokers can confidently suggest, and investors can visit only the best-matched properties. It's efficient, and above all, it’s a WIN-WIN condition."

# Process, stacks and techniques

- **Data extraction**:<br>
I used the Python library Selenium to extract informations from Plex that were sold during year 2022 on the island of Montréal, Canada. The listings were provided by a real broker from Montreal. The idea was to use real sold prices to be able to train a model to predict prices for this year listings.

- **Exploratory Data Analysis**:<br>
To be able to figure out which features to use for the modelling, I first clean the data for outliers, switch datatypes and hot-encode every non-quantitive data to be able to scale them and create a clustering using TSNE and Kmeans.

I also created some custom features to help fine-tune the model.
For example, As the saying goes, what's important in the real estate business is Location, Location, Location.
So, to be able to reflect that in my model, I calculated every average prices for each District of Montreal and create a column called "mean".

![Clustering](/output/figures/Clusters.png)
After investigating the clusters, it was clear that the type of Plex (or number of units) was indeed defining them. Within each cluster, 3 major insights help me determined the way to go:

1. The Building age
2. The Yard area (or land area)
3. Total of parkings

The more younger were the Plex the less total parking and yard area (shown by the red dashed line). Thought, using correlation technique, I figured out that Yard area and Total parking were highly correlated, so I had to eliminate one of them in the final selection.

To understand the importance of the features, I used Random Forest Classifier.

![Random forest](/output/figures/Predominant.png)
I decided to eliminate Total parking because it was less important than Yard area (as explained before). I was happy to see the "mean" column appeared here, as it reflect the importance of locations.

- **Modelling**
Using the features from the last step, I conducted multiple (iterations) linear regression using statsmodel (OLS) and sci-kit learn libraries.
It resulted with a model with an accuracy of 35%, and a deviation of 70,000$. It may seem sub-optimal, but knowing that I only used final predominant features (independant variables), for me it's a big win. Moreover, the goal was not to get the exact price, but to understand the difference between the actual and predicted price to be able to RANK the listings (recommandation system).


# Result

**Dashboard**<br>
After applying the model to a new unseen listings from actual Plex beeing on the market from a specific location (Ahuntsic), I imported the result in Tableau Destop to create a Dashboard to represent my idea of an application.
![Dashboard](/output/figures/Dashboard.png)

The Real Estate broker, after meeting with the customer, would type in and/or select the requirements. Of course, this is a static database. In the real world, my app would then interpret the text using Machine Learning techniques (potentially AI), send this information to the Real estate database, run my script and return the ranked listings to be shown here.
My rank system uses the difference between actual and predicted price and a score based on how many features correspond to the customer requirements using a weight system. Because traditionnaly, you would filter the customer requirements and then you could end up having no choice at all. But my system doesn’t filtered out the listings, it scores them and reveal the TOP 1 for each of my category:

- The bargain, under-valued
- The Mainstream, fair price
- The Premium, over-priced

# Future developpment

In this ever-evolving world of technology, there's always room for growth. Given more time, I would have dived into using Natural Language Processing to better understand customer needs. Looking ahead, I'd either learn this myself or team up with a data scientist and a web developer. 
Imagine a mobile application that instantly reads real estate databases, processes preferences, and delivers top property recommendations directly to potential buyers. Efficiency and innovation combined. So, I pose the question - are you as excited about this vision as I am? Why not give it a try!

# Tech stack

- Python
- Tableau Desktop


