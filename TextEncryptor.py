import argparse
from concrete import fhe

class TextEncryptor:
    def __init__(self):
        self.configuration = fhe.Configuration(
            enable_unsafe_features=True,
            parameter_selection_strategy=fhe.ParameterSelectionStrategy.MULTI,
            show_progress=True,
        )

    @fhe.compiler({"x": "encrypted"})
    def encrypt_decrypt_function(x):
        return x

    def encrypt(self, text):
        # Convert text to ASCII values
        ascii_values = [ord(char) for char in text]
        # Pad the input to a fixed length (e.g., 1000)
        padded_input = ascii_values + [0] * (1000 - len(ascii_values))
        
        # Create an inputset for compilation
        inputset = [(padded_input,)]
        
        # Compile the function
        circuit = self.encrypt_decrypt_function.compile(inputset, configuration=self.configuration)
        
        # Encrypt the padded input
        encrypted_data = circuit.encrypt(padded_input)
        return encrypted_data, circuit

    def decrypt(self, encrypted_data, circuit):
        # Decrypt the data
        decrypted_data = circuit.decrypt(encrypted_data)
        
        # Convert ASCII values back to text, stopping at the first 0
        decrypted_text = ''
        for value in decrypted_data:
            if value == 0:
                break
            decrypted_text += chr(int(value))
        
        return decrypted_text

def main():
    parser = argparse.ArgumentParser(description="Encrypt and decrypt text using Concrete FHE.")
    parser.add_argument("text", help="The text to encrypt and decrypt")
    args = parser.parse_args()

    encryptor = TextEncryptor()

    print("Original text:", args.text)
    
    try:
        encrypted_data, circuit = encryptor.encrypt(args.text)
        print("Text encrypted.")
        
        decrypted_text = encryptor.decrypt(encrypted_data, circuit)
        print("Decrypted text:", decrypted_text)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Please check your Concrete library version and ensure it's compatible with this code.")

if __name__ == "__main__":
    main()
