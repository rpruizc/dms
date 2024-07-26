import argparse
from concrete import fhe
import logging

logging.basicConfig(level=logging.INFO)

class TextEncryptor:
    def __init__(self, padding_length=1000):
        """
        Initialize the TextEncryptor with FHE configuration and padding length.

        :param padding_length: Length to pad the input text to. Default is 1000.
        """
        self.configuration = fhe.Configuration(
            enable_unsafe_features=True,
            parameter_selection_strategy=fhe.ParameterSelectionStrategy.MULTI,
            show_progress=True,
        )
        self.padding_length = padding_length

    @fhe.compiler({"x": "encrypted"})
    def encrypt_decrypt_function(x):
        """
        A simple encryption-decryption function that returns the input as is.

        :param x: Input data.
        :return: The input data.
        """
        return x

    def encrypt(self, text):
        """
        Encrypt the given text.

        :param text: The text to encrypt.
        :return: A tuple containing the encrypted data and the compiled circuit.
        """
        try:
            # Convert text to ASCII values
            ascii_values = [ord(char) for char in text]
            if len(ascii_values) > self.padding_length:
                raise ValueError("Text length exceeds padding length.")
            
            # Pad the input to a fixed length
            padded_input = ascii_values + [0] * (self.padding_length - len(ascii_values))
            
            # Create an inputset for compilation
            inputset = [(padded_input,)]
            
            # Compile the function
            circuit = self.encrypt_decrypt_function.compile(inputset, configuration=self.configuration)
            
            # Encrypt the padded input
            encrypted_data = circuit.encrypt(padded_input)
            return encrypted_data, circuit
        except Exception as e:
            logging.error(f"Encryption failed: {str(e)}")
            raise

    def decrypt(self, encrypted_data, circuit):
        """
        Decrypt the given encrypted data.

        :param encrypted_data: The data to decrypt.
        :param circuit: The compiled circuit used for decryption.
        :return: The decrypted text.
        """
        try:
            # Decrypt the data
            decrypted_data = circuit.decrypt(encrypted_data)
            
            # Convert ASCII values back to text, stopping at the first 0
            decrypted_text = ''.join(chr(int(value)) for value in decrypted_data if value != 0)
            
            return decrypted_text
        except Exception as e:
            logging.error(f"Decryption failed: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Encrypt and decrypt text using Concrete FHE.")
    parser.add_argument("text", help="The text to encrypt and decrypt")
    parser.add_argument("--padding_length", type=int, default=1000, help="The padding length for encryption")
    args = parser.parse_args()

    encryptor = TextEncryptor(padding_length=args.padding_length)

    logging.info(f"Original text: {args.text}")
    
    try:
        encrypted_data, circuit = encryptor.encrypt(args.text)
        logging.info("Text encrypted.")
        
        decrypted_text = encryptor.decrypt(encrypted_data, circuit)
        logging.info(f"Decrypted text: {decrypted_text}")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        logging.error("Please check your Concrete library version and ensure it's compatible with this code.")

if __name__ == "__main__":
    main()
