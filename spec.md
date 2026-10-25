# Definitions of agents and interactions

Agents are individual actors with economic goals which have a set of restrained actions which they can take in order to achieve assigned goals. Agents and goals are listed below.

## Agents

### __Firm__

Firms represent industrial concerns which work to maximise profit in their available market. Each firm is capable of producing some amount of supply units for each possible supply category. The upper limit of supply for a firm is dictated by the capacity coefficient of each firm multiplied by the labour force employed by the firm:

$$T_S = l_Sc_S$$

Where $l_S$ is the product of employees $l$ and a labor coefficent $\alpha_S$

Each firm will then present their total goods on the market at a unit price which is set internally and receive total profits from any purchases that occur. If applicable each firm will pay taxes to the appropriate authorities and then pay a wage to the workers employed at the firm. The total profit formula is as follows:

$$P = (\sum_0^S{\sigma_S\mu_St_S}) - (wl)$$

where $\sigma_S$ is the units sold in the cycle, $\mu_S$ is the unit price, $t_S$ is the inverse of the tax rate, $w$ is the wage per employee, and $L$ is the number of employees.

The firm will then adjust internal variables in order to maximise profit:

#### __Adjustment__

1. $L$, A firm can change the number of employees either through layoffs or through hiring.
2. $\mu_S$, A firm can change the unit price of the goods that they sell, per supply category.
3. $w$, A firm can change the wages of the employees.
4. $l_c$, A firm can change the labor coefficent in order to assign labor to more profitable sectors.

A firm can choose to enact any combination of changes, subject to dynamic constraints (ie, labour laws, fixed pricing, etc.) In order to estimate future profit, the quantity of future sales needs to be estimated.

##### __Labor__

A firm has two possible labor adjustments that can be made per cycle. Firstly, a firm can re adjust labor coefficents in order to assign labor to more profitable demand categories. The income that a company can generate given some vector of coefficents $\alpha$ is:

$$I(\alpha) = \sum_0^Sl\alpha_Sc_S\mu_S$$

Unless $l_Sc_S \lt \sigma_S$ (demand is less than total supply) in which case:

$$I(\alpha) = \sum_0^S\sigma_S\mu_S$$

With the constraint:

$$\sum_0^S\alpha_S = 1$$

Simply maximising $\alpha$ over this function leads to hyper specialisation, so to ensure that only gradual changes are made to the coefficents a step size is applied as a parmater of each firm.

To create a labor indicator, first the demand ratio is defined as:

$$r(l,\alpha,\sigma) = \frac{\sigma_S}{l_Sc_S}$$

This ratio defines the amount of fullfiled demand. Since $\sigma_S \le l_Sc_S$ it follows $0 \lt r \le 1$. In order to smooth hire and layoff actions firms will only trigger such an action when the ratio reaches some internal level which is specific to each firm.




##### __Price__

Assuming limited demand $d_s$ and a maximal price $\Mu_S$ that a population is willing to pay, the maximum profit is obtained by matching the productivity of the firm $lc_S$ to the demand $d_S$ and matching the unit price of the firm $\mu_S$ to $\Mu_S$. Since the optimal price $\Mu_S$ is unknown to a firm, it must estimate $\Mu_S$ with the estimator $\mu_S^*$. The method of estimation is discussed in a later section.
