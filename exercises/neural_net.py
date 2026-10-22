import torch 
import torch.nn as nn

# training data with 1 feature that is 1 column however 4 rows,  and going into 1 neuron. The number of features is the number of columns in a dataset
# so its like we are giving x input and true y inputs when x is this y is this, find the pattern, the maths rule that transforms x to y.This is supervised learning, where y is the actual target and we use the prediction from the model to fine tune the weights into learning to guess correctly based on a rule

x = torch.tensor([[1.0], [2.0], [3.0], [4.0]])
y= torch.tensor([[3.0], [5.0], [7.0], [9.0]])

# model having one input feature going to one neuron. when you write 784 by 784 each pixel is a feature since the neural net requires flattening to accept it.
model = nn.Linear(1,1)

# describe loss, Mean squared error, squared to remove the negative, prediction-target)^2
loss_fn = nn.MSELoss()

# optimizer
#update every paramter, parametrs are the learnable numbers, that is the weights and the bias, the learning rate is the step of the update.nn.Module has the parameters stored
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)

#training
for epoch in range(1000):
    prediction = model(x)
    loss = loss_fn(prediction, y)
    optimizer.zero_grad() # clear the gradients, calculate the slope each time we update the weight
    loss.backward() # autograd now computes dLoss/dWeight,dLoss/dBias and the values are stored in weight.grad and bias.grad. This tells the optimizer to move in the oppposite direction to find the lowest loss point
    optimizer.step() # new_weight = old_weight - (lr * weight*grad) does the same for bias
    
    if epoch % 100 == 0:
        print(f"Epoch {epoch}  Loss : {loss.item():.4f}")
        
print("\n learned parameters: ")
print( "This is the new weight", model.weight)
print("This is the updated bias", model.bias)

