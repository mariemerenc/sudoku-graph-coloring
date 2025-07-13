import os
import sys
import time
import json
import statistics
import csv
from typing import Dict, Any
from sudoku_board import SudokuBoard
from sudoku_solver import SimpleSudokuSolver, DSATURSudokuSolver


class SudokuExperiment:
    """Classe para gerenciar experimentos do projeto"""
    def __init__(self, input_file: str):
        self.input_file = input_file
        self.sudoku_boards = []

    def load_sudokus(self) -> bool:
        """Carrega os Sudokus do arquivo .txt"""
        
        with open(self.input_file, 'r') as file:
            content = file.read().strip()
        grids = content.split('Grid ')
        for grid_data in grids:
            if not grid_data.strip():
                continue
            lines = grid_data.strip().split('\n')
            grid_number = lines[0].strip()
            grid_lines = lines[1:10]
            if len(grid_lines) != 9:
                continue
            board = SudokuBoard()
            board.load_from_string('\n'.join(grid_lines))
            if board.is_valid():
                self.sudoku_boards.append({
                    'id': len(self.sudoku_boards) + 1,
                    'original_id': grid_number,
                    'board': board,
                })
        print(f"Carregados {len(self.sudoku_boards)} Sudokus válidos.")
        return len(self.sudoku_boards) > 0
        

    def run_solver(self, solver_type: str, num_runs: int, max_time: float = 300.0) -> Dict[str, Any]:
        """Executa um solver específico por uma determinada quantidade de vezes"""
        print(f"\n=== Executando: {solver_type.upper()} ({num_runs} execuções) ===")
        
        run_data = {
            sudoku['id']: {'times': [], 'nodes': 0, 'backtracks': 0} 
            for sudoku in self.sudoku_boards
        }

        for i in range(num_runs):
            print(f"\n--- Execução {i+1}/{num_runs} ---")
            for sudoku_data in self.sudoku_boards:
                sudoku_id = sudoku_data['id']
                board = sudoku_data['board'].copy()
                solver = SimpleSudokuSolver() if solver_type == 'simple' else DSATURSudokuSolver()

                print(f"Resolvendo Sudoku {sudoku_id:2d}...", end=" ", flush=True)
                success, solve_time = solver.solve(board)
                stats = solver.get_stats()
                
                status = "SOLVED" if success and solve_time <= max_time else ("TIMEOUT" if solve_time > max_time else "FAILED")
                run_data[sudoku_id]['times'].append(solve_time)
                
                if i == 0:  # valores determinísticos coletados apenas na primeira execução
                    run_data[sudoku_id]['nodes'] = stats['nodes_explored']
                    run_data[sudoku_id]['backtracks'] = stats['backtrack_count']
                
                print(f"{status:8s} ({solve_time:6.3f}s)")
        
        # estatísticas finais
        results = []
        total_time = total_nodes = total_backtracks = 0
        
        for sudoku_data in self.sudoku_boards:
            sudoku_id = sudoku_data['id']
            times = run_data[sudoku_id]['times']
            
            time_mean = statistics.mean(times)
            time_std_dev = statistics.stdev(times) if len(times) > 1 else 0
            
            total_time += time_mean
            total_nodes += run_data[sudoku_id]['nodes']
            total_backtracks += run_data[sudoku_id]['backtracks']

            results.append({
                'sudoku_id': sudoku_id,
                'original_id': sudoku_data['original_id'],
                'nodes_explored': run_data[sudoku_id]['nodes'],
                'backtrack_count': run_data[sudoku_id]['backtracks'],
                'time_mean': time_mean,
                'time_std_dev': time_std_dev,
                'all_times': times
            })

        total_sudokus = len(self.sudoku_boards)
        return {
            'solver_type': solver_type,
            'num_runs': num_runs,
            'total_sudokus': total_sudokus,
            'avg_time': total_time / total_sudokus,
            'avg_nodes_explored': total_nodes / total_sudokus,
            'avg_backtrack_count': total_backtracks / total_sudokus,
            'results': results
        }

    def run_comparison(self, num_runs: int, max_time: float = 300.0) -> Dict[str, Any]:
        """Executa experimento comparativo completo"""
        print(f"\n=== EXPERIMENTO COMPARATIVO ({num_runs} execuções por Sudoku) ===")
        
        simple_results = self.run_solver('simple', num_runs, max_time)
        dsatur_results = self.run_solver('dsatur', num_runs, max_time)
        
        
        return {
            'simple': simple_results,
            'dsatur': dsatur_results,
            'comparison': {
                'summary': {
                    'simple_avg_time': simple_results['avg_time'],
                    'dsatur_avg_time': dsatur_results['avg_time'],
                    'simple_avg_nodes': simple_results['avg_nodes_explored'],
                    'dsatur_avg_nodes': dsatur_results['avg_nodes_explored'],
                }
            }
        }

    def save_results(self, results: Dict[str, Any]):
        """Salva resultados em JSON e CSV"""
        ts = int(time.time())
        
        # json
        json_filename = f"results_{ts}.json"
        with open(json_filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResultados (JSON) salvos em: {json_filename}")
        
        # csv para plotagem
        csv_filename = f"plot_data_{ts}.csv"
        header = ['sudoku_id', 'original_id', 'simple_time_mean', 'simple_time_std_dev', 
                  'simple_nodes', 'simple_backtracks', 'dsatur_time_mean', 'dsatur_time_std_dev', 
                  'dsatur_nodes', 'dsatur_backtracks']
        
        with open(csv_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            
            simple_res = {r['sudoku_id']: r for r in results['simple']['results']}
            dsatur_res = {r['sudoku_id']: r for r in results['dsatur']['results']}
            
            for sid in simple_res:
                writer.writerow([
                    sid, simple_res[sid]['original_id'],
                    simple_res[sid]['time_mean'], simple_res[sid]['time_std_dev'],
                    simple_res[sid]['nodes_explored'], simple_res[sid]['backtrack_count'],
                    dsatur_res[sid]['time_mean'], dsatur_res[sid]['time_std_dev'],
                    dsatur_res[sid]['nodes_explored'], dsatur_res[sid]['backtrack_count'],
                ])
        print(f"Dados (CSV) salvos em: {csv_filename}")

    def print_summary(self, results: Dict[str, Any]):
        """Imprime resumo dos resultados"""
        simple = results['simple']
        dsatur = results['dsatur']
        
        print("\n" + "="*50)
        print("\nResolução de Sudokus com Coloração de Grafos - Comparativo entre Backtracking Simples e DSATUR")
        print("\n" + "-"*15 + "DIM0549 - Grafos" + "-"*15 + "13 de julho de 2025")
        print("\n" + "Componentes: Adriel Torquato Costa e Mariana Emerenciano Miranda")
        print("\n" + "="*50)
        print("RESUMO DOS RESULTADOS")
        print("="*50)
        print(f"Total de Sudokus: {simple['total_sudokus']} | Execuções por Sudoku: {simple['num_runs']}")
        print("-" * 50)
        print(f"{'Métrica':<25} | {'Backtracking Simples':>15} | {'DSATUR':>15}")
        print("-" * 50)
        print(f"{'Tempo médio (s)':<25} | {simple['avg_time']:15.4f} | {dsatur['avg_time']:15.4f}")
        print(f"{'Nós explorados (média)':<25} | {simple['avg_nodes_explored']:15.0f} | {dsatur['avg_nodes_explored']:15.0f}")
        print(f"{'Backtracks médios':<25} | {simple['avg_backtrack_count']:15.0f} | {dsatur['avg_backtrack_count']:15.0f}")
        print("="*50)


def main():
    """Função principal que executa experimento comparativo"""
    if len(sys.argv) != 2:
        print("Tente: python main.py <arquivo_sudokus.txt>")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Erro: Arquivo '{input_file}' não encontrado.")
        sys.exit(1)
        
    experiment = SudokuExperiment(input_file)
    if not experiment.load_sudokus():
        sys.exit(1)

    # configurações fixas
    max_time = 60.0
    num_runs = 30
    
    start_time = time.time()
    results = experiment.run_comparison(num_runs, max_time)
    total_time = time.time() - start_time
    
    experiment.print_summary(results)
    print(f"\nTempo total do experimento: {total_time:.2f}s")
    
    experiment.save_results(results)
    print("\nExperimento concluído! :)")


if __name__ == "__main__":
    main()