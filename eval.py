from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math

def eval(true, pred):

    mse = mean_squared_error(true, pred)
    rmse = math.sqrt(mse)
    mae = mean_absolute_error(true, pred)
    r2 = r2_score(true, pred)
    
    return rmse, mae, r2