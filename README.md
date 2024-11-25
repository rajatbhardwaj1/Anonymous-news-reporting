# Anonymous News Reporting System Using RuP Algorithm (Reputation Using Pseudonyms)

## Project Overview
This project is developed as part of COL707 (Introduction to Ethical Issues in Computer Science) at IIT Delhi. It is an anonymous news reporting system built upon the **Reputation Using Pseudonyms (RuP)** algorithm, which combines anonymity and reputation through cryptographic techniques. The main objective is to enable users to report news anonymously while maintaining a reputation system that prevents impersonation or malicious behavior.

## MongoDB 
-Atlas and can be accessed at: https://cloud.mongodb.com/.
- **Database Credentials:** 
   • Username: cs5200439@cse.iitd.ac.in
   • Password: ethics@project
  
## Key Features
- **Anonymous Reporting**: Allows users to report news without revealing their real identity, protecting user privacy.
- **Reputation System**: Implements a pseudonymous reputation mechanism where user identity is hidden, yet reputation is verifiable.
- **Cryptographic Techniques**: Uses asymmetric cryptography and blind signatures to provide anonymity and security.
- **Certified Pseudonyms**: Each user is assigned a unique, certified pseudonym for each time slot, ensuring a single pseudonym per user at any given time.
- **Reputation Transfer**: Reputation can be securely transferred across pseudonyms without revealing user identity.

## Threat Model
RuP mitigates two main categories of threats:
1. **Anonymity Threats**: Ensures that the real identity of users remains hidden even under scrutiny by malicious users.
2. **Reputation System Threats**: Protects against impersonation, reputation forgery, and attempts by users to create multiple identities.

## Cryptographic Building Blocks
1. **Public/Private Key Cryptography**: Used for authentication and digital signatures.
2. **Blind Signatures**: Allows a principal to sign a document without seeing its content, ensuring that user actions remain private.
3. **Certified Pseudonyms**: Pseudonyms are validated through a Pseudonym Certification Authority (PCA) to prevent users from holding multiple pseudonyms within the same time slot.

## Architecture

### Certified Pseudonym Management
- **PCA (Pseudonym Certification Authority)**: Responsible for issuing certified pseudonyms that uniquely identify users for a specific time slot.
- **Pseudonym Validity**: Each pseudonym is valid only within a particular time slot, ensuring temporary identities.
- **Blind Signature Protocol**: Users interact with the PCA using blind signatures to obtain pseudonyms without revealing their real identities.

### Reputation Transfer Mechanism
- **Transferable Reputation Voucher (TRV)**: Allows users to carry over reputation information across pseudonyms without disclosing their identity.
- **Anonymity and Endorsement**: Involves two phases where reputation information is anonymized and endorsed under a new pseudonym by the PCA.

## Installation and Setup
To set up and run the anonymous news reporting system locally, follow these steps:

1. **Clone the Repository**
   ```bash
   git clone https://github.com/rajatbhardwaj1/Anonymous-news-reporting.git
   cd Anonymous-news-reporting
   ```

2. **Install Dependencies**
   
   In the backed folder
   
   ```bash
   pip install -r requirements.txt
   ```
   In the client folder
   ```bash
   npm install
   ```
   

3. **Run the Application**
   ```bash
   cd backend
   ```
   ```bash
   python app.py
   ```
   open another terminal
   ```bash
   cd client
   ```
   ```bash
   npm start
   ```

## Usage
1. **Register with a Pseudonym**: Users obtain a pseudonym certified by the PCA.
2. **Submit News Anonymously**: Users can report news anonymously while building a pseudonymous reputation.
3. **View Reputation**: Users can view their pseudonym's reputation within the system, transferred securely across pseudonyms when required.

## Additional Notes
- **Time Slot Validity**: The duration of a pseudonym's validity balances reputation accuracy and user anonymity.
- **Security Assumptions**: It is assumed that users do not collude, and the PCA is trusted not to associate real identities with pseudonyms.
- **Blind Signature Security**: The security model relies on the unforgeability of the blind signature protocol and the user's private keys.

## References
The project builds upon cryptographic methods and concepts from various publications:
- Chaum, D. (1983). Blind signatures for untraceable payments. Advances in Cryptology.
- Miranda, H., & Rodrigues, L. (2008). A framework to provide anonymity in reputation systems. Universidade de Lisboa.

