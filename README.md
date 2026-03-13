# Analyseur C avec Graphe de Flux de Contrôle

Un analyseur syntaxique (parser) pour le langage C écrit en Python pur, capable de générer des graphes de flux de contrôle (CFG).

## 🚀 Fonctionnalités

- **Analyse lexicale** : Tokenisation du code C
- **Analyse syntaxique** : Construction d'AST (Arbre Syntaxique Abstrait)
- **Génération CFG** : Graphes de flux de contrôle pour chaque fonction
- **Interface CLI** : Ligne de commande avec options flexibles
- **Support complet C** : Variables, fonctions, boucles, conditions, expressions
- **100% Python** : Aucune dépendance externe

## 📋 Prérequis

- Python 3.7+
- Aucune dépendance externe

## 🔧 Installation

```bash
git clone https://github.com/votre-username/analyseur-c.git
cd analyseur-c
```

## 📖 Utilisation

### Analyse basique
```bash
py main.py examples/factorial.c
```

### Options avancées
```bash
# Afficher l'AST et le CFG
py main.py -a -c examples/fibonacci.c

# Mode verbose avec statistiques
py main.py -v examples/simple.c

# Analyser du code directement
py main.py --code "int main(){return 0;}"

# Afficher les jetons
py main.py -t examples/factorial.c
```

### Toutes les options
- `-a, --afficher-ast` : Afficher l'Arbre Syntaxique Abstrait
- `-c, --afficher-cfg` : Afficher le Graphe de Flux de Contrôle
- `-s, --afficher-statistiques` : Afficher les statistiques CFG
- `-t, --afficher-jetons` : Afficher les jetons lexicaux
- `-v, --verbose` : Sortie détaillée
- `-q, --silencieux` : Sortie minimale
- `-C, --code` : Analyser une chaîne de code

## 📂 Structure du projet

```
analyseur-c/
├── main.py           # Point d'entrée et CLI
├── lexer.py          # Analyseur lexical (tokenisation)
├── parser.py         # Analyseur syntaxique (AST)
├── ast_nodes.py      # Définitions des nœuds AST
├── cfg.py            # Générateur de CFG
├── examples/         # Exemples de programmes C
│   ├── simple.c
│   ├── factorial.c
│   └── fibonacci.c
├── requirements.txt  # Dépendances (aucune)
├── .gitignore        # Fichiers à ignorer
└── README.md         # Cette documentation
```

## 📊 Exemple de sortie

```
CFG pour la fonction 'factorial':
==================================================
Entrée: Noeud0
Sortie: Noeud1

Nœuds:
  Noeud0(entree): Entry: factorial
  Noeud1(sortie): Exit: factorial
  Noeud2(condition): if ((n <= 1))
  Noeud3(retour): return 1
  Noeud4(retour): return (n * factorial((n - 1)))

Arêtes:
  0 -> 2
  2 -> 3 [vrai]
  2 -> 4 [faux]
  3 -> 1
  4 -> 1

Statistiques pour 'factorial':
  Nœuds: 5
  Arêtes: 5
  Complexité cyclomatique: 2
  Points de décision: 1
```

## 🎯 Constructions C supportées

- **Types** : `int`, `float`, `double`, `char`, `void`, `bool`
- **Structures de contrôle** : `if/else`, `while`, `for`
- **Instructions** : `return`, `break`, `continue`
- **Expressions** : Arithmétiques, logiques, comparaisons
- **Fonctions** : Définitions, appels, paramètres
- **Variables** : Déclarations, assignations

## 🧪 Tests

Le projet inclut des exemples de test dans le dossier `examples/` :

```bash
# Tester tous les exemples
py main.py examples/*.c

# Test avec statistiques détaillées
py main.py -v -s examples/fibonacci.c
```

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -am 'Ajout fonctionnalité'`)
4. Push sur la branche (`git push origin feature/amelioration`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier LICENSE pour plus de détails.

## 👥 Auteurs

- Votre nom - *Développement initial*

## 🙏 Remerciements

- Inspiré par les techniques d'analyse statique
- Merci à la communauté Python

## 📁 Structure du projet

```
projet/
├── main.py           # Point d'entrée principal
├── lexer.py          # Analyseur lexical (tokenizer)
├── parser.py         # Analyseur syntaxique 
├── ast_nodes.py      # Définitions des nœuds AST
├── cfg.py           # Générateur de CFG
└── examples/        # Exemples de programmes C
    ├── simple.c     # Fonction basique
    ├── factorial.c  # Récursion
    ├── fibonacci.c  # Boucle while
    ├── search.c     # Boucle for + array
    └── complex.c    # Structures imbriquées
```

## 🧪 Tests rapides

```bash
# Test lexer seul
python lexer.py

# Test parser seul  
python parser.py

# Test CFG seul
python cfg.py

# Test complet
python main.py examples/factorial.c
```

## 📊 Fonctionnalités supportées

### ✅ Structures C supportées
- **Types** : int, float, double, char, void, bool
- **Fonctions** : définition avec paramètres et retour
- **Instructions** : if/else, while, for, return, break, continue
- **Expressions** : arithmétiques, logiques, relationnelles
- **Déclarations** : variables avec initialisation
- **Appels** : fonctions avec arguments
- **Tableaux** : accès avec []

### 📈 CFG généré
- Nœuds typés (entry, exit, condition, statement, call, break, continue, return)
- Arêtes étiquetées (true/false pour conditions)
- Gestion correcte des boucles et break/continue
- Statistiques (complexité cyclomatique, points de décision)

## 🎯 Exemples de sortie

**Fichier `examples/factorial.c` :**
```c
int factorial(int n) {
    if (n <= 1) {
        return 1;
    } else {
        return n * factorial(n - 1);
    }
}
```

**Commande :** `python main.py examples/factorial.c`

**Sortie :**
```
Reading file: examples/factorial.c
Parsed successfully: 1 functions found
Generated 1 CFGs

CFG for function 'factorial':
==================================================
Entry: Node0
Exit: Node1

Nodes:
  Node0(entry): Entry: factorial
  Node1(exit): Exit: factorial  
  Node2(condition): if ((n <= 1))
  Node3(return): return 1
  Node4(return): return (n * factorial(n - 1))

Edges:
  0 -> 2
  2 -> 3 [true]
  2 -> 4 [false]  
  3 -> 1
  4 -> 1

Statistics for 'factorial':
  Nodes: 5
  Edges: 5
  Node types:
    condition: 1
    entry: 1
    exit: 1
    return: 2
  Cyclomatic complexity: 2
  Decision points: 1
```

## 🛠️ Architecture technique

- **Lexer** : Analyseur lexical fait maison avec gestion des commentaires
- **Parser** : Récursif descendant avec précédence des opérateurs
- **AST** : Arbre syntaxique abstrait avec types Python (dataclasses)
- **CFG** : Construction par parcours récursif de l'AST
- **Pas de dépendances** : 100% Python standard

Idéal pour l'apprentissage, l'analyse statique simple ou l'enseignement des CFG !