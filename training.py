import torch

class Trainer():
    def __init__(self, generator, discriminator, optim_g, optim_d, lambda_weight, critic_iterations, device):
        self.generator = generator
        self.discriminator = discriminator
        self.optim_g = optim_g
        self.optim_d = optim_d
        self.lambda_weight = lambda_weight
        self.critic_iterations = critic_iterations
        self.losses = {"d": [], "g": [], "gp": [], "gradient_norm": []}
        self.num_steps = 0
        self.generator = self.generator.to(device)
        self.discriminator = self.discriminator.to(device)
    
    def critic_train_step(self, x, y, lookback, output_dim, device):
        fake_data = self.generator(x)
        fake_data = torch.cat([y[:, :lookback, :], fake_data.reshape(-1, 1, output_dim)], axis=1)

        critic_real = self.discriminator(y)
        critic_fake = self.discriminator(fake_data)

        gp = self.gradient_penalty(y, fake_data, device)
        self.losses['gp'].append(gp.item())

        self.optim_d.zero_grad()
        d_loss = critic_fake.mean() - critic_real.mean() + gp
        d_loss.backward()

        self.optim_d.step()

        self.losses['d'].append(d_loss.item())
    
    def generator_train_step(self, x, y, lookback, output_dim):
        fake_data = self.generator(x)
        fake_data = torch.cat([y[:, :lookback, :], fake_data.reshape(-1, 1, output_dim)], axis=1)

        critic_fake = self.discriminator(fake_data)

        self.optim_g.zero_grad()
        g_loss = -critic_fake.mean()
        g_loss.backward()

        self.optim_g.step()

        self.losses['g'].append(g_loss.item())
    
    def gradient_penalty(self, real_data, fake_data, device):
        batch_size = real_data.size(0)
        alpha = torch.rand(batch_size, 1, 1).to(device)

        interpolated = (alpha * real_data.data + (1 - alpha) * fake_data.data.requires_grad_(True)).to(device)

        prob_interpolated = self.discriminator(interpolated)

        gradients = torch.autograd.grad(outputs=prob_interpolated, inputs=interpolated,
                                        grad_outputs=torch.ones(prob_interpolated.size()).to(device),
                                        create_graph=True, retain_graph=True)[0]

        gradients = gradients.view(batch_size, -1)
        self.losses['gradient_norm'].append(gradients.norm(2, dim=1).mean().item())

        gradients_norm = torch.sqrt(torch.sum(gradients ** 2, dim=1) + 1e-12)

        return self.lambda_weight * ((gradients_norm - 1) ** 2).mean()
    
    def train(self, data_loader, epochs, lookback, output_dim, device):
        for epoch in range(epochs):
            for x, y in data_loader:
                x, y = x.to(device), y.to(device)
                
                for _ in range(self.critic_iterations):
                    self.critic_train_step(x, y, lookback, output_dim, device)
                
                self.generator_train_step(x, y, lookback, output_dim)
                
                self.num_steps += 1
                
            print(f"Epoch [{epoch+1}/{epochs}] | D Loss: {self.losses['d'][-1]:.4f} | G Loss: {self.losses['g'][-1]:.4f} | GP: {self.losses['gp'][-1]:.4f} | Grad Norm: {self.losses['gradient_norm'][-1]:.4f}")
    

    
    
