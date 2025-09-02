import torch

class Trainer():
    def __init__(self, generator, discriminator, optim_g, optim_d, lambda_weight, critic_iterations, use_cuda=False):
        self.generator = generator
        self.discriminator = discriminator
        self.optim_g = optim_g
        self.optim_d = optim_d
        self.lambda_weight = lambda_weight
        self.critic_iterations = critic_iterations
        self.losses = {"d": [], "g": [], "gp": [], "gradient_norm": []}
        self.num_steps = 0
        self.use_cuda = use_cuda
        if self.use_cuda:
            self.generator = self.generator.cuda()
            self.discriminator = self.discriminator.cuda()
    
    def critic_train_step(self, x, y, lookback, output_dim):
        fake_data = self.generator(x)
        fake_data = torch.cat([y[:, :lookback, :], fake_data.reshape(-1, 1, output_dim)], axis=1)

        critic_real = self.discriminator(y)
        critic_fake = self.discriminator(fake_data)

        gp = self.gradient_penalty(y, fake_data)
        self.losses['GP'].append(gp.item())

        self.optim_d.zero_grad()
        d_loss = critic_fake.mean() - critic_real.mean() + gp
        d_loss.backward()

        self.optim_d.step()

        self.losses['D'].append(d_loss.item())
    
    def generator_train_step(self, x, y, lookback, output_dim):
        fake_data = self.generator(x)
        fake_data = torch.cat([y[:, :lookback, :], fake_data.reshape(-1, 1, output_dim)], axis=1)

        critic_fake = self.discriminator(fake_data)

        self.optim_g.zero_grad()
        g_loss = -critic_fake.mean()
        g_loss.backward()

        self.optim_g.step()

        self.losses['G'].append(g_loss.item())
    
    def gradient_penalty(self, real_data, fake_data):
        batch_size = real_data.size(0)
        alpha = torch.rand(batch_size, 1, 1)
        if self.use_cuda:
            alpha = alpha.cuda()

        interpolated = alpha * real_data.data + (1 - alpha) * fake_data.data.requires_grad_(True)
        if self.use_cuda:
            interpolated = interpolated.cuda()

        prob_interpolated = self.discriminator(interpolated)

        gradients = torch.autograd.grad(outputs=prob_interpolated, inputs=interpolated,
                                        grad_outputs=torch.ones(prob_interpolated.size()).cuda() if self.use_cuda else torch.ones(
                                        prob_interpolated.size()),
                                        create_graph=True, retain_graph=True)[0]

        gradients = gradients.view(batch_size, -1)
        self.losses['gradient_norm'].append(gradients.norm(2, dim=1).mean().item())

        gradients_norm = torch.sqrt(torch.sum(gradients ** 2, dim=1) + 1e-12)

        return self.lambda_weight * ((gradients_norm - 1) ** 2).mean()
    
    def train(self, data_loader, epochs, lookback, output_dim):
        for epoch in range(epochs):
            for i, (x, y) in enumerate(data_loader):
                if self.use_cuda:
                    x, y = x.cuda(), y.cuda()
                
                for _ in range(self.critic_iterations):
                    self.critic_train_step(x, y, lookback, output_dim)
                
                self.generator_train_step(x, y, lookback, output_dim)
                
                self.num_steps += 1
                
            print(f"Epoch [{epoch+1}/{epochs}] | D Loss: {self.losses['D'][-1]:.4f} | G Loss: {self.losses['G'][-1]:.4f} | GP: {self.losses['GP'][-1]:.4f} | Grad Norm: {self.losses['gradient_norm'][-1]:.4f}")
    

    
    
