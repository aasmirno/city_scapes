# Definitons of agents and interactions

Agents are individual actors with economic goals which have a set of restrained actions which they can take in order to acheive assigned goals. Agents and goals are listed below.

## Agents

### __Firm__

Firms represent industrial concerns which work to maximise profit in their avaliable market. Each firm is capable of producing some amount of supply units for each possible supply category. The upper limit of supply for a firm is dictated by the capacity coefficent of each firm multiplied by the labor force employed by the firm:

$$T_S = c_S*L$$

Where $L$ is the number of employees and $c_S$ is the capacity per supply category S.

Each firm will then present their total goods on the market at a unit price which is set internally and receive total profits from any purchases that occur. If applicable each firm will pay taxes to the appropriate authorities and then pay a wage to the workers employed at the firm. The total profit formula is as follows:

$$P = (\sum_0^S{\sigma_S\mu_St_S}) - (wL)$$

where $\sigma_S$ is the units sold in the cycle, $\mu_S$ is the unit price, $t_S$ is the inverse of the tax rate, $w$ is the wage per employee, and $L$ is the number of employees.

The firm will then whether or no to make adjustments, which are categorised as follows:

#### __Adjustment__

1. $L$, A firm can change the number of employees either through layoffs or through hiring.
2. $\mu_S$, A firm can change the unit price of the goods that they sell, per supply category.
3. $w$, A firm can change the wages of the employees.

A firm can choose to enact any combination of changes, subject to dynamic constraints (ie, labor laws, fixed pricing, etc.) In order to estimate future profit, the quantity of future sales needs to be estimated.

The problem then becomes how to analyse the expected changes in profit based on changes in levers. Looking at the formula for profit:

$$P = (\sum_0^S{\sigma_S^*\mu_St_S}) - (wL)$$

We can see that in order to account for the adjustment costs of changing labor, we need to express $\sigma_S$ as a factor of $L$. Therefore we can state the perfect profit formula:

$$\sigma_S^* \le c_SL$$

$$P \le L(\sum_0^S{c_S\mu_St_S}) - wL$$

This follows from the first formula for the upper limit of supply.

Likewise, the cost of increasing the unit price $\mu_S$ needs to be present on the expense side of the formula. This unit price cost can be expressed with the term:

$$\mu_S - \tau_S$$

Which represents the opportunity cost of a different price, ie the sales which were not made due to the current unit price. This potential revenue term can be estimated based on a number of approaches, in this model, the average income of the target population is used to estimate the price that a target population is willing to pay, represented by $\tau_S$. The profit formula becomes:

$$P \le L(\sum_0^S{c_S\mu_St_S}) - wL - \sum_0^S(\mu_S-\tau_S)$$

Partial Derivatives:

$$\frac{dP}{dL} = \sum_0^S{c_S\mu_St_S}$$

$$\frac{dP}{d\mu} = L\sum_0^S{c_St_S} - \tau_S$$

$$\frac{dP}{dw} = L$$

#### __Avoiding the simple case__

When a firm decides to increase $L$ it must put a hiring order to the population pool to which it is attached. This prevents preferential treatment for firms who put in their hiring orders first. Each pop unit who is looking for employment will then assess all possible positions and choose the one that fulfils their economic goal, which will include assessment of wages promised by a firm. This introduces a negative consequence to lowering wages and should prevent firms from simply lowering wages to increase profit. Populations will also make choices on which industry to purchase goods from based on unit price, which should have the same effect of preventing firms from simply increasing prices to maximise profit.
