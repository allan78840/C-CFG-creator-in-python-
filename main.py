"""
Analyseur C avec génération de Graphe de Flux de Contrôle (CFG)
Point d'entrée principal
"""

import sys
import argparse
from pathlib import Path

from lexer import tokeniser, ErreurAnalyseurLexical
from parser import analyser, ErreurAnalyseurSyntaxique
from ast_nodes import *
from cfg import construire_cfg, GrapheFluxControle

def afficher_ast(programme: Programme) -> None:
    """Afficher l'AST de manière lisible"""
    print("\n" + "="*50)
    print("ARBRE SYNTAXIQUE ABSTRAIT")
    print("="*50)
    
    for i, fonction in enumerate(programme.fonctions, 1):
        print(f"\n{i}. Fonction: {fonction.nom}")
        print(f"   Type de retour: {fonction.type_retour.value}")
        print(f"   Paramètres: {len(fonction.parametres)}")
        for parametre in fonction.parametres:
            print(f"     - {parametre.nom}: {parametre.type_parametre.value}")
        
        print(f"   Corps: {type(fonction.corps).__name__}")
        if isinstance(fonction.corps, Bloc):
            print(f"     Instructions: {len(fonction.corps.instructions)}")
            for j, instruction in enumerate(fonction.corps.instructions[:5], 1):  # Max 5 premières
                type_instruction = type(instruction).__name__
                print(f"       {j}. {type_instruction}")
            if len(fonction.corps.instructions) > 5:
                print(f"       ... et {len(fonction.corps.instructions) - 5} de plus")

def afficher_jetons(jetons) -> None:
    """Afficher les jetons"""
    print("\n" + "="*50)
    print("JETONS")
    print("="*50)
    
    for i, jeton in enumerate(jetons[:30], 1):  # Max 30 premiers jetons
        if jeton.type.name != "NOUVELLE_LIGNE":  # Ignorer les nouvelles lignes pour la clarté
            print(f"{i:2}. {jeton}")
    
    if len(jetons) > 30:
        print(f"... et {len(jetons) - 30} jetons de plus")

def afficher_statistiques_cfg(cfg: GrapheFluxControle) -> None:
    """Afficher les statistiques d'un CFG"""
    print(f"\nStatistiques pour '{cfg.nom_fonction}':")
    print(f"  Nœuds: {len(cfg.noeuds)}")
    print(f"  Arêtes: {len(cfg.aretes)}")
    
    # Compter par type de nœud
    types_noeuds = {}
    for noeud in cfg.noeuds.values():
        types_noeuds[noeud.type_noeud] = types_noeuds.get(noeud.type_noeud, 0) + 1
    
    print("  Types de nœuds:")
    for type_noeud, compteur in sorted(types_noeuds.items()):
        print(f"    {type_noeud}: {compteur}")
    
    # Analyser la complexité
    conditions = sum(1 for noeud in cfg.noeuds.values() if noeud.type_noeud == "condition")
    print(f"  Complexité cyclomatique: {len(cfg.aretes) - len(cfg.noeuds) + 2}")
    print(f"  Points de décision: {conditions}")

def analyser_fichier(nom_fichier: str, arguments) -> None:
    """Analyser un fichier C complet"""
    try:
        # Lecture du fichier
        with open(nom_fichier, 'r', encoding='utf-8') as f:
            code = f.read()
        
        print(f"Lecture du fichier: {nom_fichier}")
        print(f"Taille du fichier: {len(code)} caractères")
        
        # Tokenisation
        if arguments.afficher_jetons:
            print(f"\nTokenisation...")
        
        jetons = tokeniser(code)
        
        if arguments.afficher_jetons:
            print(f"Génération de {len(jetons)} jetons")
            afficher_jetons(jetons)
        
        # Analyse syntaxique
        if arguments.afficher_ast or arguments.verbose:
            print(f"\nAnalyse syntaxique...")
        
        programme = analyser(jetons)
        
        print(f"Analyse réussie: {len(programme.fonctions)} fonctions trouvées")
        
        if arguments.afficher_ast:
            afficher_ast(programme)
        
        # Génération CFG
        if arguments.verbose:
            print(f"\nConstruction des Graphes de Flux de Contrôle...")
        
        cfgs = construire_cfg(programme)
        
        print(f"{len(cfgs)} CFGs générés")
        
        # Affichage des CFG
        for cfg in cfgs:
            if arguments.afficher_cfg:
                cfg.afficher_graphe()
            
            if arguments.afficher_statistiques or arguments.verbose:
                afficher_statistiques_cfg(cfg)
        
        # Résumé final
        if not arguments.silencieux:
            print("\n" + "="*50)
            print("RÉSUMÉ")  
            print("="*50)
            print(f"Fichier: {nom_fichier}")
            print(f"Fonctions: {len(programme.fonctions)}")
            print(f"Total nœuds CFG: {sum(len(cfg.noeuds) for cfg in cfgs)}")
            print(f"Total arêtes CFG: {sum(len(cfg.aretes) for cfg in cfgs)}")
            
            # Fonctions trouvées
            print("\nFonctions trouvées:")
            for fonction in programme.fonctions:
                nb_parametres = len(fonction.parametres)
                print(f"  - {fonction.nom}({nb_parametres} params) -> {fonction.type_retour.value}")
        
    except FileNotFoundError:
        print(f"Erreur: Fichier '{nom_fichier}' non trouvé")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Erreur: Impossible de décoder le fichier '{nom_fichier}' en UTF-8")
        sys.exit(1)
    except ErreurAnalyseurLexical as e:
        print(f"Erreur Analyseur Lexical: {e}")
        sys.exit(1)
    except ErreurAnalyseurSyntaxique as e:
        print(f"Erreur Analyseur Syntaxique: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        if arguments.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def analyser_chaine(code: str, arguments) -> None:
    """Analyser du code C fourni directement"""
    try:
        print("Analyse du code fourni...")
        print(f"Longueur du code: {len(code)} caractères")
        
        # Tokenisation
        jetons = tokeniser(code) 
        if arguments.afficher_jetons:
            afficher_jetons(jetons)
        
        # Analyse syntaxique
        programme = analyser(jetons)
        print(f"Analyse réussie: {len(programme.fonctions)} fonctions")
        
        if arguments.afficher_ast:
            afficher_ast(programme)
        
        # CFG
        cfgs = construire_cfg(programme)
        print(f"{len(cfgs)} CFGs générés")
        
        for cfg in cfgs:
            if arguments.afficher_cfg:
                cfg.afficher_graphe()
            if arguments.afficher_statistiques:
                afficher_statistiques_cfg(cfg)
        
    except (ErreurAnalyseurLexical, ErreurAnalyseurSyntaxique) as e:
        print(f"Erreur: {e}")
        sys.exit(1)

def main():
    """Point d'entrée principal"""
    analyseur_args = argparse.ArgumentParser(
        description="Analyseur C avec génération de Graphe de Flux de Contrôle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  %(prog)s examples/factorielle.c              # Analyse basique
  %(prog)s -v examples/factorielle.c           # Sortie détaillée
  %(prog)s -a -c examples/factorielle.c        # Afficher AST et CFG
  %(prog)s -s examples/*.c                     # Statistiques pour plusieurs fichiers
  %(prog)s --code 'int f(){return 42;}'        # Analyser chaîne de code
        """
    )
    
    # Arguments principaux
    groupe = analyseur_args.add_mutually_exclusive_group(required=True)
    groupe.add_argument('fichiers', nargs='*', help='Fichiers sources C à analyser')
    groupe.add_argument('--code', '-C', type=str, help='Chaîne de code C à analyser')
    
    # Options d'affichage
    analyseur_args.add_argument('--afficher-jetons', '-t', action='store_true', 
                       help='Afficher les jetons de l\'analyseur lexical')
    analyseur_args.add_argument('--afficher-ast', '-a', action='store_true',
                       help='Afficher l\'Arbre Syntaxique Abstrait')  
    analyseur_args.add_argument('--afficher-cfg', '-c', action='store_true',
                       help='Afficher le Graphe de Flux de Contrôle')
    analyseur_args.add_argument('--afficher-statistiques', '-s', action='store_true',
                       help='Afficher les statistiques CFG')
    
    # Options de verbosité
    analyseur_args.add_argument('--verbose', '-v', action='store_true',
                       help='Sortie détaillée')
    analyseur_args.add_argument('--silencieux', '-q', action='store_true',
                       help='Sortie minimale')
    
    arguments = analyseur_args.parse_args()
    
    # Si pas d'options d'affichage spécifiées, mode par défaut
    if not any([arguments.afficher_jetons, arguments.afficher_ast, arguments.afficher_cfg, arguments.afficher_statistiques, arguments.verbose]):
        arguments.afficher_cfg = True  # Afficher le CFG par défaut
        arguments.afficher_statistiques = True
    
    # Traitement
    if arguments.code:
        # Code fourni en ligne de commande
        analyser_chaine(arguments.code, arguments)
    else:
        # Fichiers
        if not arguments.fichiers:
            analyseur_args.print_help()
            sys.exit(1)
        
        for nom_fichier in arguments.fichiers:
            if len(arguments.fichiers) > 1:
                print(f"\n{'='*60}")
                print(f"Traitement: {nom_fichier}")
                print(f"{'='*60}")
            
            analyser_fichier(nom_fichier, arguments)

if __name__ == "__main__":
    main()