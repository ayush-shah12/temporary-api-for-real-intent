# Zapier Integration API - MVP

This is a basic testing API developed to explore integration with Zapier. It serves as an MVP (Minimum Viable Product) to assess the viability of the integration approach, and will be further developed into a production-ready API in the very near future. 

Real-Intent doesn't have any usecase(currently) for a accessible API like this, so this will be very basic, and geared towards offering flexibility for Zapier development.

### Key Features:
- **Authentication**: Users authenticate using a unique, randomly generated API key uuid4 (OAuth2 will be implemented once the integration is finalized). 
- **Webhook Management**: Stores webhooks created when clients set up a 'zap' (via `/subscribe`) and notifies when a zap is turned off or deleted (via `/unsubscribe`).
    - For now its stored on an AWS postgres db, but it's not ideal, as we don't have any other usecase for this db other than managing webhooks. Look into ways where we can store this information somewhere else, possibly Stripe if they support additional fields since client info is pulled from there anyway. That way this API could directly send it to Stripe, and that would eliminate the need for a database and would keep the delivery process the same as the webhook can then be pulled with Stripe, instead of querying the database.  

### Flow:
1. **Authentication**:
   - Clients authenticate through the unique API key we provide them before creating a zap.
2. **Using Templates**:
   - Clients can use our pre-configured templates or build upon them.
3. **Lead Trigger**:
   - Our app provides a single trigger, which is a webhook that sends clients' leads on a weekly basis.
4. **End Process**:
   - Once the client authenticates once, no other action needs to be taken on either side. Will implement a ZapierDeliverer in Real Intent SDK to manage the automatic delivery to webhooks once the app is developed.

### Template Ideas:
- **CRM Integrations**: For all CRMs not supported natively.
- **Spreadsheets**: Excel, Google Sheets, etc.
- **Email Workflows**: Integrating email services, automatic forwarding to other addresses, etc...
- **Lead Routing**: Routing leads to sub agents if it's a company getting multiple batches.
---

This project is meant to help us test the integration with Zapier before moving forward with a fully-fledged production API.
