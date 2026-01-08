from generics import TreeNode
from decimal import Decimal

class AVLTree:

    """
    AVLTree is a self-balancing binary search tree for managing ordered PriceLevel data.

    Public Methods:
        - insert(node): Insert a TreeNode into the AVL tree.
        - search(price): Search for a PriceLevel by price using binary search.

    Internal Methods:
        _insert(node, root): Recursive helper for insertion with rebalancing.
        _balance_tree(root): Rebalances the subtree rooted at the given node.
        _rotate_left(node): Performs a left rotation around the given node.
        _rotate_right(node): Performs a right rotation around the given node.
        _get_balance(node): Computes the balance factor of a node.
        _get_height(node): Returns the height of a node.
        _search(price, root): Recursive binary search by price.
 
    """

    def __init__(self, root : TreeNode | None = None ) -> None:
        self.root = root 
    
    def delete(self, node : TreeNode) : 
        self.root = self._delete(node, self.root) 

    def _delete(self, node : TreeNode, root : TreeNode | None ) :

        if root is None : 
            return root  

        if node.value < root.value : 
            root.left = self._delete(node, root.left)

        elif node.value > root.value : 
            root.right = self._delete(node, root.right)

        else : 
            if root.left is None : 
                return root.right 
            elif root.right is None :
                return root.left 

            pred = self._greatest_child(root.left)
            root.value = pred.value 
            root.left = self._delete(pred, root.left)

        return self._balance_tree(root)
       
    def _greatest_child(self, start : TreeNode) : 

        if start.left is None and start.right is None : 
            return start 
        
        if start.right: 
            return self._greatest_child(start.right) 
        
        return start 

    def insert(self, node : TreeNode) : 
        self.root = self._insert(node, self.root)

    def _insert(self, node : TreeNode, root : TreeNode | None): 
        if root is None:
            node.height = 0 # ensure height is zero 
            return node
        
        if node.value <= root.value : 
            root.left = self._insert(node, root.left)
        else : 
            root.right = self._insert(node, root.right)

        left_height = self._get_height(root.left) 
        right_height = self._get_height(root.right)     
        root.height = 1 + max(left_height, right_height)

        # once added 
        # check my balance factor 

        balance_factor = self._get_balance(root) 
        if abs(balance_factor) > 1 : 
            # This guarntees that there are two other node below the root and we can balance 
            root = self._balance_tree(root)

        return root

    def _get_balance(self, node : TreeNode | None ) : 
        if node is None : 
            return -1 

        left_height = self._get_height(node.left)
        right_height = self._get_height(node.right)

        return left_height - right_height 

    def _balance_tree(self, root : TreeNode | None) : 
        if root : 
            
            balance = self._get_balance(root)

            if balance > 1 :
                # Left Heavy tree  
                if self._get_balance(root.left) < 0 :
                    root.left = self._rotate_left(root.left)

                return self._rotate_right(root)

            if balance < -1 : 
                # Right heavy tree 
                if self._get_balance(root.right) > 0 : 
                    root.right = self._rotate_right(root.right)

                return self._rotate_left(root)

        return root 

    
    def _get_height(self, node: TreeNode | None) -> int:
        return node.height if node else -1


    def _rotate_left(self, node : TreeNode | None) :
        if node :  

            right_node = node.right 
            if not right_node : 
                return node 

            subtree = right_node.left 

            right_node.left = node
            node.right = subtree

            node.height = 1 + max(self._get_height(node.left), self._get_height(node.right)) 
            right_node.height = 1 + max( self._get_height(right_node.left), self._get_height(right_node.right))

            return right_node

        return node 
            
    
    def _rotate_right(self, node : TreeNode | None) : 
        if node : 
            left_node = node.left 
            if not left_node : 
                return node 

            subtree = left_node.right 

            left_node.right = node 
            node.left = subtree

            node.height = 1 + max(self._get_height(node.left), self._get_height(node.right)) 
            left_node.height = 1 + max(self._get_height(left_node.left), self._get_height(left_node.right)) 

            return left_node
        
        return node

    def search(self, price : Decimal) : 
        return self._search(price, self.root)

    def _search(self, price : Decimal, root : TreeNode | None ) : 
        if root is None : 
            return None 
        if root.value.price == price :
            return root.value 
        
        if price <= root.value.price : 
            return self._search(price, root.left)
        return self._search(price, root.right)


__all__ = ["AVLTree"]
