# Write-up Template

### Analyze, choose, and justify the appropriate resource option for deploying the app.

*For **both** a VM or App Service solution for the CMS app:*
- *Analyze costs, scalability, availability, and workflow*
- *Choose the appropriate solution (VM or App Service) for deploying the app*
- *Justify your choice*

**Cost** *: Virtual Machines are more expensive due to maintenance, storage, and compute costs, with payment required for the entire uptime, even when idle. In contrast, Azure App Service uses a pay-as-you-go pricing model, making it more cost-efficient, and offers a free tier (F1) for small-scale applications.*

**Scalability** *: Virtual Machines require manual scaling, involving the configuration and maintenance of VM scale sets. Azure App Service, however, includes built-in auto-scaling managed by Azure, simplifying the process.*

**Availability** *: Virtual Machines need availability sets or zones to ensure uptime and redundancy. Azure App Service provides high availability by default, with built-in failover and redundancy, reducing the need for additional configuration.*

**Workflow** *: Virtual Machines offer more control over the operating system and environment, allowing custom configurations. However, this comes with the added responsibility of managing updates, security, and patches. Azure App Service abstracts away infrastructure concerns, offering a fully managed solution that allows developers to focus solely on the application.*


*I opted for Azure App Service due to its cost efficiency compared to the VM service, particularly since I utilized the free F1 tier, which is a significant advantage. The workflow with App Service is generally easier to deploy via the portal, and its integration with GitHub saves time and simplifies the process. Using a virtual machine would have required additional funds for a continuously running instance. Additionally, App Service offers auto-scaling capabilities and high availability without needing extra configuration for issues like failover or redundancy.*


### Assess app changes that would change your decision.

*Detail how the app and any other needs would have to change for you to change your decision in the last section.* 

**If the project demands greater control over the infrastructure, such as custom OS-level configurations, enhanced security measures, or running background processes, a Virtual Machine would be more suitable. This also applies to intensive computational tasks requiring direct server access or hosting a multi-component system with multiple services on a single machine. However, for a straightforward CMS where quick, scalable, and cost-effective deployment is desired, Azure App Service remains the best choice.**
