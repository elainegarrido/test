import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.patches as patches

class VetorLabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("VetorLab - Laboratório de Transformações Lineares")
        self.root.geometry("1100x750")
        
        # Configuração inicial
        self.dimension = tk.StringVar(value="2D")
        self.vector_inputs = []
        self.transformation_matrix = []
        self.animation = None
        self.step_by_step = False
        
        # Criar widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame de controle
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Frame de visualização
        viz_frame = ttk.LabelFrame(main_frame, text="Visualização", padding="10")
        viz_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Controles de dimensão
        ttk.Label(control_frame, text="Dimensão:").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="2D", variable=self.dimension, value="2D", 
                       command=self.update_dimension).grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(control_frame, text="3D", variable=self.dimension, value="3D", 
                       command=self.update_dimension).grid(row=0, column=2, sticky=tk.W)
        
        # Entrada de vetores
        self.vector_frame = ttk.LabelFrame(control_frame, text="Vetor de Entrada", padding="10")
        self.vector_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=tk.W)
        self.create_vector_inputs()
        
        # Transformação matricial
        ttk.Label(control_frame, text="Matriz de Transformação:").grid(row=2, column=0, columnspan=3, sticky=tk.W)
        self.matrix_frame = ttk.Frame(control_frame)
        self.matrix_frame.grid(row=3, column=0, columnspan=3, pady=5, sticky=tk.W)
        self.create_matrix_inputs()
        
        # Controle de animação
        ttk.Label(control_frame, text="Animação:").grid(row=4, column=0, sticky=tk.W)
        self.animation_speed = tk.DoubleVar(value=1.0)
        ttk.Scale(control_frame, from_=0.5, to=3.0, variable=self.animation_speed, 
                  orient=tk.HORIZONTAL, length=100).grid(row=4, column=1, columnspan=2, sticky=tk.W)
        
        # Botões de ação
        ttk.Button(control_frame, text="Aplicar Transformação", command=self.apply_transformation).grid(
            row=5, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        self.step_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Passo a Passo", variable=self.step_var).grid(
            row=6, column=0, columnspan=3, pady=5)
        
        ttk.Button(control_frame, text="Gerar Exercício Aleatório", command=self.generate_random_exercise).grid(
            row=7, column=0, columnspan=3, pady=10, sticky=tk.EW)
        
        ttk.Button(control_frame, text="Questionário Avaliativo", command=self.show_questionnaire).grid(
            row=8, column=0, columnspan=3, pady=5, sticky=tk.EW)
        
        # Área de visualização
        self.fig = plt.figure(figsize=(7, 7), tight_layout=True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=viz_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Área de explicação
        explanation_frame = ttk.Frame(viz_frame)
        explanation_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.explanation_var = tk.StringVar(value="Insira um vetor e uma matriz de transformação para começar")
        explanation_label = ttk.Label(explanation_frame, textvariable=self.explanation_var, 
                                     wraplength=600, justify=tk.LEFT, padding=(5, 5))
        explanation_label.pack(fill=tk.X)
        
        # Status bar
        self.status_var = tk.StringVar(value="Pronto")
        ttk.Label(control_frame, textvariable=self.status_var).grid(row=9, column=0, columnspan=3, pady=10)
        
        # Inicializar plot
        self.update_plot()
    
    def create_vector_inputs(self):
        # Limpar inputs existentes e redefinir lista
        for widget in self.vector_frame.winfo_children():
            widget.destroy()
        self.vector_inputs = []
        
        # Criar novos inputs baseados na dimensão
        dim = 2 if self.dimension.get() == "2D" else 3
        
        for i in range(dim):
            ttk.Label(self.vector_frame, text=f"Componente {i+1}:").grid(row=i, column=0, padx=5, pady=2)
            entry = ttk.Entry(self.vector_frame, width=10)
            entry.insert(0, "0.0")
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.vector_inputs.append(entry)
    
    def create_matrix_inputs(self):
        # Limpar inputs existentes e redefinir lista
        for widget in self.matrix_frame.winfo_children():
            widget.destroy()
        self.transformation_matrix = []
        
        # Criar novos inputs baseados na dimensão
        dim = 2 if self.dimension.get() == "2D" else 3
        
        for i in range(dim):
            row = []
            for j in range(dim):
                entry = ttk.Entry(self.matrix_frame, width=8)
                entry.insert(0, "1.0" if i == j else "0.0")
                entry.grid(row=i, column=j, padx=2, pady=2)
                row.append(entry)
            self.transformation_matrix.append(row)
    
    def update_dimension(self):
        self.create_vector_inputs()
        self.create_matrix_inputs()
        self.update_plot()
    
    def get_vector(self):
        try:
            # Verificar se as entradas ainda existem antes de acessá-las
            valid_entries = []
            for entry in self.vector_inputs:
                try:
                    # Testar se o widget ainda existe
                    entry.winfo_exists()
                    valid_entries.append(entry)
                except tk.TclError:
                    continue
            
            return [float(entry.get()) for entry in valid_entries]
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos para o vetor.")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar entradas: {str(e)}")
            return None
    
    def get_matrix(self):
        try:
            matrix = []
            for row in self.transformation_matrix:
                matrix_row = []
                for entry in row:
                    try:
                        # Verificar se o widget ainda existe
                        entry.winfo_exists()
                        matrix_row.append(float(entry.get()))
                    except tk.TclError:
                        continue
                if matrix_row:  # Só adicionar se a linha não estiver vazia
                    matrix.append(matrix_row)
            return matrix
        except ValueError:
            messagebox.showerror("Erro", "Por favor, insira valores numéricos para a matriz.")
            return None
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao acessar matriz: {str(e)}")
            return None
    
    def apply_transformation(self):
        vector = self.get_vector()
        matrix = self.get_matrix()
        
        if vector is None or matrix is None:
            return
        
        # Verificar se as dimensões são compatíveis
        if len(vector) != len(matrix) or any(len(row) != len(vector) for row in matrix):
            messagebox.showerror("Erro", "Dimensões incompatíveis entre vetor e matriz")
            return
        
        # Aplicar transformação
        try:
            transformed_vector = np.dot(matrix, vector)
        except ValueError:
            messagebox.showerror("Erro", "Dimensões incompatíveis para multiplicação matriz-vetor")
            return
        
        # Atualizar visualização
        self.update_plot(vector, transformed_vector, matrix)
        
        # Atualizar status
        self.status_var.set(f"Transformação aplicada: {transformed_vector}")
        
        # Gerar explicação
        self.generate_explanation(vector, matrix, transformed_vector)
        
        # Animar se necessário
        if self.step_var.get():
            self.animate_transformation(vector, matrix, transformed_vector)
    
    def generate_explanation(self, vector, matrix, transformed_vector):
        dim = len(vector)
        
        explanation = "Transformação Linear:\n"
        explanation += f"Vetor original: v = {vector}\n"
        explanation += f"Matriz de transformação: A = \n"
        
        for i in range(dim):
            explanation += "[" + "  ".join([f"{x:.2f}" for x in matrix[i]]) + "]\n"
        
        explanation += "\nOperação realizada: Av = \n"
        
        # Mostrar cálculo passo a passo
        for i in range(dim):
            terms = [f"{matrix[i][j]:.2f}×{vector[j]:.2f}" for j in range(dim)]
            result = sum(matrix[i][j] * vector[j] for j in range(dim))
            explanation += f"= ({' + '.join(terms)}) = {result:.2f}\n"
        
        explanation += f"\nResultado: Av = {transformed_vector}"
        
        self.explanation_var.set(explanation)
    
    def animate_transformation(self, original_vector, matrix, transformed_vector):
        # Parar qualquer animação existente
        if self.animation is not None:
            try:
                self.animation.event_source.stop()
            except:
                pass
        
        dim = len(original_vector)
        
        # Configurar animação
        self.fig.clf()
        
        if dim == 2:
            ax = self.fig.add_subplot(111)
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.axhline(0, color='black', linewidth=0.5)
            ax.axvline(0, color='black', linewidth=0.5)
            ax.grid(True)
            ax.set_title('Transformação Linear - Animação')
            ax.set_xlabel('Eixo X')
            ax.set_ylabel('Eixo Y')
            
            # Vetores base
            base_x = np.array([1, 0])
            base_y = np.array([0, 1])
            trans_base_x = np.dot(matrix, base_x)
            trans_base_y = np.dot(matrix, base_y)
            
            # Elementos de animação
            orig_vector_plot = ax.quiver(0, 0, 0, 0, color='blue', scale=1, scale_units='xy', angles='xy')
            trans_vector_plot = ax.quiver(0, 0, 0, 0, color='red', scale=1, scale_units='xy', angles='xy')
            base_x_plot = ax.quiver(0, 0, 0, 0, color='gray', scale=1, scale_units='xy', angles='xy')
            base_y_plot = ax.quiver(0, 0, 0, 0, color='gray', scale=1, scale_units='xy', angles='xy')
            trans_base_x_plot = ax.quiver(0, 0, 0, 0, color='green', linestyle='--', scale=1, scale_units='xy', angles='xy')
            trans_base_y_plot = ax.quiver(0, 0, 0, 0, color='green', linestyle='--', scale=1, scale_units='xy', angles='xy')
            
            # Adicionar legendas
            ax.legend([orig_vector_plot, trans_vector_plot, trans_base_x_plot], 
                     ['Vetor Original', 'Vetor Transformado', 'Base Transformada'],
                     loc='upper right')
            
            # Função de animação
            def update(frame):
                progress = frame / 100
                
                # Vetor original (estático)
                orig_vector_plot.set_UVC(original_vector[0], original_vector[1])
                
                # Base transformada animada
                current_base_x = base_x * (1 - progress) + trans_base_x * progress
                current_base_y = base_y * (1 - progress) + trans_base_y * progress
                
                base_x_plot.set_UVC(current_base_x[0], current_base_x[1])
                base_y_plot.set_UVC(current_base_y[0], current_base_y[1])
                trans_base_x_plot.set_UVC(current_base_x[0], current_base_x[1])
                trans_base_y_plot.set_UVC(current_base_y[0], current_base_y[1])
                
                # Vetor transformado animado
                current_transformed = np.array(original_vector) * (1 - progress) + np.array(transformed_vector) * progress
                trans_vector_plot.set_UVC(current_transformed[0], current_transformed[1])
                
                return orig_vector_plot, trans_vector_plot, base_x_plot, base_y_plot, trans_base_x_plot, trans_base_y_plot
            
            # Criar animação
            self.animation = FuncAnimation(self.fig, update, frames=100, 
                                          interval=20/self.animation_speed.get(), 
                                          blit=True)
            
        else:  # 3D
            ax = self.fig.add_subplot(111, projection='3d')
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_zlim(-5, 5)
            ax.set_title('Transformação Linear 3D - Animação')
            ax.set_xlabel('Eixo X')
            ax.set_ylabel('Eixo Y')
            ax.set_zlabel('Eixo Z')
            
            # Função de animação
            def update(frame):
                ax.cla()
                ax.set_xlim(-5, 5)
                ax.set_ylim(-5, 5)
                ax.set_zlim(-5, 5)
                ax.set_title('Transformação Linear 3D - Animação')
                ax.set_xlabel('Eixo X')
                ax.set_ylabel('Eixo Y')
                ax.set_zlabel('Eixo Z')
                
                progress = frame / 100
                
                # Plotar base canônica
                base_vectors = np.eye(3)
                for i in range(3):
                    ax.quiver(0, 0, 0, base_vectors[0][i], base_vectors[1][i], base_vectors[2][i], 
                             color='gray', linestyle='-', linewidth=1, arrow_length_ratio=0.1)
                
                # Plotar base transformada animada
                trans_base_vectors = np.dot(matrix, base_vectors)
                for i in range(3):
                    current_vec = base_vectors[:, i] * (1 - progress) + trans_base_vectors[:, i] * progress
                    ax.quiver(0, 0, 0, current_vec[0], current_vec[1], current_vec[2], 
                             color='green', linestyle='--', linewidth=1, arrow_length_ratio=0.1)
                
                # Plotar vetores
                ax.quiver(0, 0, 0, original_vector[0], original_vector[1], original_vector[2], 
                         color='blue', linewidth=2, arrow_length_ratio=0.1, label='Original')
                
                current_transformed = np.array(original_vector) * (1 - progress) + np.array(transformed_vector) * progress
                ax.quiver(0, 0, 0, current_transformed[0], current_transformed[1], current_transformed[2], 
                         color='red', linewidth=2, arrow_length_ratio=0.1, label='Transformado')
                
                ax.legend()
                return ax
            
            # Criar animação
            self.animation = FuncAnimation(self.fig, update, frames=100, 
                                          interval=20/self.animation_speed.get())
        
        self.canvas.draw()
    
    def update_plot(self, original_vector=None, transformed_vector=None, matrix=None):
        self.fig.clf()
        
        dim = 2 if self.dimension.get() == "2D" else 3
        
        # Configurar plot
        if dim == 2:
            ax = self.fig.add_subplot(111)
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.axhline(0, color='black', linewidth=0.5)
            ax.axvline(0, color='black', linewidth=0.5)
            ax.grid(True)
            ax.set_title('Transformação Linear 2D')
            ax.set_xlabel('Eixo X')
            ax.set_ylabel('Eixo Y')
            
            # Plotar grade de fundo com menor opacidade
            for x in range(-5, 6):
                ax.axvline(x, color='lightgray', linestyle='-', alpha=0.3)
            for y in range(-5, 6):
                ax.axhline(y, color='lightgray', linestyle='-', alpha=0.3)
            
            # Plotar base canônica original
            ax.quiver(0, 0, 1, 0, angles='xy', scale_units='xy', scale=1, 
                     color='gray', width=0.005, label='Base Original')
            ax.quiver(0, 0, 0, 1, angles='xy', scale_units='xy', scale=1, 
                     color='gray', width=0.005)
            
            # Adicionar rótulos aos eixos
            ax.text(5.2, 0, 'X', fontsize=12, ha='center', va='center')
            ax.text(0, 5.2, 'Y', fontsize=12, ha='center', va='center')
            
            if original_vector is not None and transformed_vector is not None:
                # Plotar vetores
                ax.quiver(0, 0, original_vector[0], original_vector[1], 
                         angles='xy', scale_units='xy', scale=1, color='blue', 
                         width=0.015, label='Original')
                ax.quiver(0, 0, transformed_vector[0], transformed_vector[1], 
                         angles='xy', scale_units='xy', scale=1, color='red', 
                         width=0.015, label='Transformado')
                
                # Adicionar rótulos aos vetores
                ax.text(original_vector[0]/2, original_vector[1]/2, 'v', 
                        fontsize=12, color='blue', ha='center', va='center')
                ax.text(transformed_vector[0]/2, transformed_vector[1]/2, 'Av', 
                        fontsize=12, color='red', ha='center', va='center')
                
                # Plotar transformação da base canônica
                if matrix is not None:
                    base_x = np.array([1, 0])
                    base_y = np.array([0, 1])
                    trans_base_x = np.dot(matrix, base_x)
                    trans_base_y = np.dot(matrix, base_y)
                    
                    ax.quiver(0, 0, trans_base_x[0], trans_base_x[1], 
                             angles='xy', scale_units='xy', scale=1, color='green', 
                             width=0.010, linestyle='--', label='Base Transformada')
                    ax.quiver(0, 0, trans_base_y[0], trans_base_y[1], 
                             angles='xy', scale_units='xy', scale=1, color='green', 
                             width=0.010, linestyle='--')
                    
                    # Adicionar rótulos à base transformada
                    ax.text(trans_base_x[0]/2, trans_base_x[1]/2, 'A·i', 
                            fontsize=10, color='green', ha='center', va='center')
                    ax.text(trans_base_y[0]/2, trans_base_y[1]/2, 'A·j', 
                            fontsize=10, color='green', ha='center', va='center')
                    
                    # Desenhar paralelogramo para mostrar combinação linear
                    points = np.array([
                        [0, 0],
                        trans_base_x * original_vector[0],
                        trans_base_x * original_vector[0] + trans_base_y * original_vector[1],
                        trans_base_y * original_vector[1]
                    ])
                    
                    polygon = patches.Polygon(points, closed=True, 
                                             fill=True, alpha=0.1, color='purple')
                    ax.add_patch(polygon)
            
            ax.legend(loc='upper right')
            
        else:  # 3D
            ax = self.fig.add_subplot(111, projection='3d')
            ax.set_xlim(-5, 5)
            ax.set_ylim(-5, 5)
            ax.set_zlim(-5, 5)
            ax.set_title('Transformação Linear 3D')
            ax.set_xlabel('Eixo X')
            ax.set_ylabel('Eixo Y')
            ax.set_zlabel('Eixo Z')
            
            # Plotar base canônica original
            ax.quiver(0, 0, 0, 1, 0, 0, color='gray', linestyle='-', linewidth=1, arrow_length_ratio=0.1, label='Base Original')
            ax.quiver(0, 0, 0, 0, 1, 0, color='gray', linestyle='-', linewidth=1, arrow_length_ratio=0.1)
            ax.quiver(0, 0, 0, 0, 0, 1, color='gray', linestyle='-', linewidth=1, arrow_length_ratio=0.1)
            
            if original_vector is not None and transformed_vector is not None:
                # Plotar vetores 3D
                ax.quiver(0, 0, 0, original_vector[0], original_vector[1], original_vector[2], 
                         color='blue', linewidth=2, arrow_length_ratio=0.1, label='Original')
                ax.quiver(0, 0, 0, transformed_vector[0], transformed_vector[1], transformed_vector[2], 
                         color='red', linewidth=2, arrow_length_ratio=0.1, label='Transformado')
                
                # Adicionar rótulos
                ax.text(original_vector[0], original_vector[1], original_vector[2], 'v', 
                        fontsize=12, color='blue', ha='center', va='center')
                ax.text(transformed_vector[0], transformed_vector[1], transformed_vector[2], 'Av', 
                        fontsize=12, color='red', ha='center', va='center')
                
                # Plotar transformação da base canônica
                if matrix is not None:
                    base_vectors = np.eye(3)
                    trans_base_vectors = np.dot(matrix, base_vectors)
                    
                    for i in range(3):
                        ax.quiver(0, 0, 0, trans_base_vectors[0][i], trans_base_vectors[1][i], trans_base_vectors[2][i], 
                                 color='green', linestyle='--', linewidth=1, arrow_length_ratio=0.1, 
                                 label='Base Transformada' if i == 0 else "")
                        
                        # Adicionar rótulos
                        vec = trans_base_vectors[:, i]
                        ax.text(vec[0], vec[1], vec[2], f'A·e{i+1}', 
                                fontsize=10, color='green', ha='center', va='center')
            
            ax.legend()
        
        self.canvas.draw()
    
    def generate_random_exercise(self):
        dim = 2 if self.dimension.get() == "2D" else 3
        
        # Gerar vetor aleatório
        random_vector = np.random.uniform(-3, 3, dim).round(1)
        for i, entry in enumerate(self.vector_inputs):
            try:
                entry.delete(0, tk.END)
                entry.insert(0, str(random_vector[i]))
            except tk.TclError:
                continue
        
        # Gerar matriz de transformação aleatória
        random_matrix = np.random.uniform(-2, 2, (dim, dim)).round(1)
        for i in range(dim):
            for j in range(dim):
                try:
                    entry = self.transformation_matrix[i][j]
                    entry.delete(0, tk.END)
                    entry.insert(0, str(random_matrix[i,j]))
                except (IndexError, tk.TclError):
                    continue
        
        # Calcular vetor transformado
        transformed_vector = np.dot(random_matrix, random_vector)
        
        # Atualizar visualização
        self.update_plot(random_vector, transformed_vector, random_matrix)
        
        # Gerar explicação
        self.generate_explanation(random_vector, random_matrix, transformed_vector)
        
        self.status_var.set("Exercício aleatório gerado")
    
    def show_questionnaire(self):
        questionnaire_window = tk.Toplevel(self.root)
        questionnaire_window.title("Questionário Avaliativo")
        questionnaire_window.geometry("500x400")
        
        ttk.Label(questionnaire_window, text="Questionário Avaliativo", font=('Arial', 14, 'bold')).pack(pady=10)
        
        questions = [
            "1. Como você avalia a clareza da representação visual das operações?",
            "2. A animação passo a passo ajuda a entender as transformações lineares?",
            "3. As explicações textuais são úteis para compreender os cálculos?",
            "4. Qual a utilidade geral que você atribui à plataforma VetorLab no seu aprendizado?"
        ]
        
        options = [
            ["a) Muito clara", "b) Clara", "c) Pouco clara", "d) Confusa"],
            ["a) Ajuda muito", "b) Ajuda", "c) Pouco ajuda", "d) Não ajuda"],
            ["a) Muito úteis", "b) Úteis", "c) Pouco úteis", "d) Inúteis"],
            ["a) Muito Útil", "b) Útil", "c) Pouco Útil", "d) Inútil"]
        ]
        
        self.answers = []
        
        for i, (question, opts) in enumerate(zip(questions, options)):
            frame = ttk.Frame(questionnaire_window)
            frame.pack(fill=tk.X, padx=10, pady=5)
            
            ttk.Label(frame, text=question, wraplength=450).pack(anchor=tk.W)
            
            var = tk.StringVar()
            self.answers.append(var)
            
            for opt in opts:
                ttk.Radiobutton(frame, text=opt, variable=var, value=opt[0]).pack(anchor=tk.W)
        
        ttk.Button(questionnaire_window, text="Enviar Respostas", 
                  command=lambda: self.submit_questionnaire(questionnaire_window)).pack(pady=20)
    
    def submit_questionnaire(self, window):
        answers = [var.get() for var in self.answers]
        if all(answers):
            messagebox.showinfo("Obrigado", "Obrigado por responder o questionário!")
            window.destroy()
        else:
            messagebox.showerror("Erro", "Por favor, responda todas as perguntas.")

if __name__ == "__main__":
    root = tk.Tk()
    app = VetorLabApp(root)
    root.mainloop()