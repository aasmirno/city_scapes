# Definitions of agents and interactions

Agents are individual actors with economic goals which have a set of restrained actions which they can take in order to achieve assigned goals. Agents and goals are listed below.

## Agents

### __Firm__

Firms represent industrial concerns which work to maximise profit in their available market. Each firm is capable of producing some amount of supply units for each possible supply category. The upper limit of supply for a firm is dictated by the capacity coefficient of each firm multiplied by the labour force employed by the firm:

$$T_S = l_Sc_S$$

Where $l_S$ is the product of employees $l$ and a labor coefficent $\alpha_S$

Each firm will then present their total goods on the market at a unit price which is set internally and receive total profits from any purchases that occur. If applicable each firm will pay taxes to the appropriate authorities and then pay a wage to the workers employed at the firm. The total profit formula is as follows:

$$P = \sum_0^S{\sigma_S\mu_St_S} - wl$$

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

To calculate the expected utility of changing the labor pool we use a partial derivative of the profit function:

$$\frac{dP}{dL} = -l$$

When supply is greater than demand and:

$$\frac{dP}{dL} = \sum_0^S{\alpha_Sc_S\mu_St_S} - w$$

When demand is greater than supply.

This means that the utility gained in firing a worker is equal to the wage that is paid to the worker if supply outstrips demand, and is equal to the potential income of hiring a worker minus the wage that is paid. Demand is estimated using the methods discussed later.

##### __Price__

Assuming limited demand $d_s$ and a maximal price $\Mu_S$ that a population is willing to pay, the maximum profit is obtained by matching the productivity of the firm $lc_S$ to the demand $d_S$ and matching the unit price of the firm $\mu_S$ to $\Mu_S$. Since the optimal price $\Mu_S$ is unknown to a firm, it must estimate $\Mu_S$ with the estimator $\mu_S^*$. The method of estimation is discussed in a later section.

### __Consumer__

A consumer is a market participant and generator of demand. Each consumer has a set of demands for each supply category and an avaliable money supply with which to try and fulfil the demand. Every market cycle, each consumer participating in the market will generate an order, which will contain the number of units demanded and the maximum price which a consumer if willing to pay. The form looks as follows:

$$D_S = (units, price_{max})$$

The market will then attempt to fulfill the orders according to market rules.

#### __Demand__

Consumer demand will be affected by 