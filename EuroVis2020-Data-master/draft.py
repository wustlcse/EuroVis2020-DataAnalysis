import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import datasets, linear_model
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
sns.set_theme(style="ticks")

df = sns.load_dataset("penguins")
print(df)
# # Load the diabetes dataset
# # diabetes_X, diabetes_y = datasets.load_diabetes(return_X_y=True)
# # print('y')
# # print(diabetes_X.shape,diabetes_y.shape)
# #
# # # Use only one feature
# # diabetes_X = diabetes_X[:, np.newaxis, 2]
#
# # Split the data into training/testing sets
#

x = np.array([[5, 15, 25, 35, 45, 55],[3, 12, 28, 35, 44, 51], [4,5,6,20,23,34]])
df2 = pd.DataFrame(x,columns=['a', 'b', 'c','d','e','f'])
print(df2)

sns.pairplot(df2, hue="f")
plt.show()


# y = np.array([5, 20,23])
# print(y)
#
# diabetes_X_train = x
# diabetes_X_test = np.array([[5, 18, 22, 30, 40, 59], [3, 12, 28, 35, 44, 51], [6,12,16,18,26,50]])
#
# # Split the targets into training/testing sets
# diabetes_y_train = y
# diabetes_y_test = np.array([5, 27,30])
#
# # Create linear regression object
# regr = linear_model.LinearRegression()
#
# # Train the model using the training sets
# regr.fit(diabetes_X_train, diabetes_y_train)
#
#
#
# # Make predictions using the testing set
# diabetes_y_pred = regr.predict(diabetes_X_test)
# print(diabetes_y_pred)
#
# # The coefficients
# print('Coefficients: \n', regr.coef_)
# # The mean squared error
# print('Mean squared error: %.2f'
#       % mean_squared_error(diabetes_y_test, diabetes_y_pred))
# # The coefficient of determination: 1 is perfect prediction
# print('Coefficient of determination: %.2f'
#       % r2_score(diabetes_y_test, diabetes_y_pred))
#
# # Plot outputs
# plt.scatter(diabetes_X_test[:,5], diabetes_y_test,  color='black')
# plt.plot(diabetes_X_test[:,5], diabetes_y_pred, color='blue', linewidth=3)
#
# plt.xticks(())
# plt.yticks(())
#
# plt.show()