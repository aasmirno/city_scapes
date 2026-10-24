# Definitons of agents and interactions

Agents are individual actors with economic goals which have a set of restrained actions which they can take in order to acheive assigned goals. Agents and goals are listed below.

## Agents

### __Firm__

Firms represent industrial concerns which work to maximise profit in their avaliable market. Each firm is capable of producing some amount of supply units for each possible supply category. The upper limit of supply for a firm is dictated by the capacity coefficent of each firm multiplied by the labor force employed by the firm:

$$T_S = lc_S$$

Where $L$ is the number of employees and $c_S$ is the capacity per supply category S.

Each firm will then present their total goods on the market at a unit price which is set internally and receive total profits from any purchases that occur. If applicable each firm will pay taxes to the appropriate authorities and then pay a wage to the workers employed at the firm. The total profit formula is as follows:

$$P = (\sum_0^S{\sigma_S\mu_St_S}) - (wL)$$

where $\sigma_S$ is the units sold in the cycle, $\mu_S$ is the unit price, $t_S$ is the inverse of the tax rate, $w$ is the wage per employee, and $L$ is the number of employees.

The firm will then adjust internal variables in order to maximise profit:

#### __Adjustment__

1. $L$, A firm can change the number of employees either through layoffs or through hiring.
2. $\mu_S$, A firm can change the unit price of the goods that they sell, per supply category.
3. $w$, A firm can change the wages of the employees.

A firm can choose to enact any combination of changes, subject to dynamic constraints (ie, labor laws, fixed pricing, etc.) In order to estimate future profit, the quantity of future sales needs to be estimated.

Assuming limited demand $d_s$ and a maximal price $\tau_S$ that a population is willing to pay, the maximum profit is obtained by matching the productivity of the firm $lc_S$ to the demand $d_S$ and matching the unit price of the firm $\mu_S$ to $\tau_S$.

Since the optimal price $\tau_S$ is unknown to a firm, it must estimate $\tau_S$ with the estimator $\tau_S^*$. The method of estimation is discussed in a later section. In order to achieve optimal labor costs, the firm must have some target profit margin and manage labor and wages such that the profit margin is met. Since $\tau_S^*$ is known at this stage, the cost of increasing or decreasing labor can found from the profit function:

$$P = \tau_S$$


#### __Avoiding the simple case__

When a firm decides to increase $L$ it must put a hiring order to the population pool to which it is attached. This prevents preferential treatment for firms who put in their hiring orders first. Each pop unit who is looking for employment will then assess all possible positions and choose the one that fulfils their economic goal, which will include assessment of wages promised by a firm. This introduces a negative consequence to lowering wages and should prevent firms from simply lowering wages to increase profit. Populations will also make choices on which industry to purchase goods from based on unit price, which should have the same effect of preventing firms from simply increasing prices to maximise profit.
