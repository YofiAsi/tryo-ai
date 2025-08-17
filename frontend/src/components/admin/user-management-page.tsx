"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { 
  Users, 
  Plus, 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  UserCheck, 
  UserX,
  Search,
  Filter,
  RefreshCw,
  Loader2
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { SidebarTrigger } from "@/components/ui/sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Label } from "@/components/ui/label"
import { useAdminUsers, useAdminMutations, revalidateAllData } from "@/hooks/use-swr-hooks"
import { UserRole } from "@/lib/api/enums"
import { UserDTO } from "@/lib/api/types"
import { toast } from "@/components/ui/use-toast"

interface NewUser {
  name: string
  email: string
  role: UserRole
}

export function UserManagementPage() {
  const [searchTerm, setSearchTerm] = useState("")
  const [statusFilter, setStatusFilter] = useState("all")
  const [roleFilter, setRoleFilter] = useState("all")
  const [isAddUserOpen, setIsAddUserOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<UserDTO | null>(null)
  const [isEditUserOpen, setIsEditUserOpen] = useState(false)
  const [newUser, setNewUser] = useState<NewUser>({
    name: "",
    email: "",
    role: UserRole.USER
  })
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  // Use SWR hooks for data fetching
  const { 
    data: users = [], 
    error: usersError, 
    isLoading: usersLoading,
    isValidating: usersValidating 
  } = useAdminUsers(1, 100)

  const { createUser, changeUserStatus, updateUser, deleteUser } = useAdminMutations()

  // Filter users based on search term and filters
  const filteredUsers = users.filter((user) => {
    const matchesSearch =
      user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email?.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesStatus = statusFilter === "all" || (statusFilter === "active" ? user.is_active : !user.is_active)
    const matchesRole = roleFilter === "all" || user.role === roleFilter
    return matchesSearch && matchesStatus && matchesRole
  })

  const handleAddUser = async () => {
    setActionLoading('add')
    try {
      await createUser({
        name: newUser.name,
        email: newUser.email,
        role: newUser.role as UserRole
      })
      setNewUser({ name: "", email: "", role: UserRole.USER })
      setIsAddUserOpen(false)
      toast({
        title: "User added",
        description: `User "${newUser.name}" has been added.`,
      })
    } catch (error) {
      console.error("Failed to create user:", error)
      toast({
        title: "Failed to add user",
        description: "Could not add user. Please try again.",
        variant: "destructive",
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleRetry = async () => {
    try {
      await revalidateAllData()
    } catch (error) {
      console.error('Failed to retry:', error)
    }
  }

  const handleEditUser = (user: UserDTO) => {
    setEditingUser(user)
    setIsEditUserOpen(true)
  }

  const handleUpdateUser = async () => {
    if (!editingUser) return
    
    setActionLoading('edit')
    try {
      await updateUser(editingUser.id, {
        name: editingUser.name || '',
        email: editingUser.email || '',
        role: editingUser.role || UserRole.USER
      })
      setEditingUser(null)
      setIsEditUserOpen(false)
      toast({
        title: "User updated",
        description: `User "${editingUser.name}" has been updated.`,
      })
    } catch (error) {
      console.error("Failed to update user:", error)
      toast({
        title: "Failed to update user",
        description: "Could not update user. Please try again.",
        variant: "destructive",
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    setActionLoading(`status-${userId}`)
    try {
      await changeUserStatus(userId, !currentStatus)
      toast({
        title: currentStatus ? "User deactivated" : "User activated",
        description: `User has been ${currentStatus ? 'deactivated' : 'activated'}.`,
      })
    } catch (error) {
      console.error("Failed to change user status:", error)
      toast({
        title: "Failed to change status",
        description: "Could not change user status. Please try again.",
        variant: "destructive",
      })
    } finally {
      setActionLoading(null)
    }
  }

  const handleDeleteUser = async (userId: string) => {
    if (!confirm('Are you sure you want to delete this user? This action cannot be undone.')) {
      return
    }
    
    setActionLoading(`delete-${userId}`)
    try {
      await deleteUser(userId)
      toast({
        title: "User deleted",
        description: `User has been deleted.`,
      })
    } catch (error) {
      console.error("Failed to delete user:", error)
      toast({
        title: "Failed to delete user",
        description: "Could not delete user. Please try again.",
        variant: "destructive",
      })
    } finally {
      setActionLoading(null)
    }
  }

  const getRoleBadgeVariant = (role: string | undefined) => {
    switch (role) {
      case "admin":
        return "destructive"
      case "manager":
        return "default"
      case "user":
        return "secondary"
      default:
        return "outline"
    }
  }

  const getStatusBadgeVariant = (status: boolean) => {
    switch (status) {
      case true:
        return "default"
      case false:
        return "secondary"
      default:
        return "outline"
    }
  }

  // Handle loading state
  if (usersLoading) {
    return (
      <div className="flex h-screen flex-col">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-b bg-background px-6 py-4"
        >
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <div>
              <h1 className="text-2xl font-bold">User Management</h1>
              <p className="text-muted-foreground">Manage system users and permissions</p>
            </div>
          </div>
        </motion.header>
        
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto" />
            <p className="text-gray-600">Loading users...</p>
          </div>
        </div>
      </div>
    )
  }

  // Handle error state
  if (usersError) {
    return (
      <div className="flex h-screen flex-col">
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="border-b bg-background px-6 py-4"
        >
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <div>
              <h1 className="text-2xl font-bold">User Management</h1>
              <p className="text-muted-foreground">Manage system users and permissions</p>
            </div>
          </div>
        </motion.header>
        
        <div className="flex-1 flex items-center justify-center p-6">
          <div className="text-center space-y-4">
            <p className="text-lg text-muted-foreground mb-4">
              {usersError?.message || 'Failed to load users. Please try again.'}
            </p>
            <Button onClick={handleRetry}>Try Again</Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b bg-background px-6 py-4"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <SidebarTrigger />
            <div>
              <h1 className="text-2xl font-bold">User Management</h1>
              <p className="text-muted-foreground">Manage system users and permissions</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button 
              onClick={handleRetry} 
              variant="outline" 
              size="sm"
              disabled={usersLoading}
              className="gap-2"
            >
              <RefreshCw className={`h-4 w-4 ${usersValidating ? 'animate-spin' : ''}`} />
              {usersValidating ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Dialog open={isAddUserOpen} onOpenChange={setIsAddUserOpen}>
              <DialogTrigger asChild>
                <Button className="gap-2">
                  <Plus className="h-4 w-4" />
                  Add User
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Add New User</DialogTitle>
                  <DialogDescription>
                    Create a new user account with the specified role and permissions.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="name">Name</Label>
                    <Input
                      id="name"
                      value={newUser.name}
                      onChange={(e) => setNewUser(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="Enter full name"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      value={newUser.email}
                      onChange={(e) => setNewUser(prev => ({ ...prev, email: e.target.value }))}
                      placeholder="Enter email address"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="role">Role</Label>
                    <Select value={newUser.role} onValueChange={(value) => setNewUser(prev => ({ ...prev, role: value as UserRole }))}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value={UserRole.USER}>User</SelectItem>
                        <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsAddUserOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleAddUser} disabled={actionLoading === 'add'}>
                    {actionLoading === 'add' ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Adding...
                      </>
                    ) : (
                      'Add User'
                    )}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        </div>
      </motion.header>

      {/* Edit User Dialog */}
      <Dialog open={isEditUserOpen} onOpenChange={setIsEditUserOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>
              Update user account information and permissions.
            </DialogDescription>
          </DialogHeader>
          {editingUser && (
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="edit-name">Name</Label>
                <Input
                  id="edit-name"
                  value={editingUser.name || ''}
                  onChange={(e) => setEditingUser(prev => prev ? { ...prev, name: e.target.value } : null)}
                  placeholder="Enter full name"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-email">Email</Label>
                <Input
                  id="edit-email"
                  type="email"
                  value={editingUser.email || ''}
                  onChange={(e) => setEditingUser(prev => prev ? { ...prev, email: e.target.value } : null)}
                  placeholder="Enter email address"
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="edit-role">Role</Label>
                <Select 
                  value={editingUser.role || UserRole.USER} 
                  onValueChange={(value) => setEditingUser(prev => prev ? { ...prev, role: value as UserRole } : null)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value={UserRole.USER}>User</SelectItem>
                    <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditUserOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateUser} disabled={actionLoading === 'edit'}>
              {actionLoading === 'edit' ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Updating...
                </>
              ) : (
                'Update User'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Main Content */}
      <div className="flex-1 overflow-auto p-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="space-y-6"
        >
          {/* Filters */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Users ({filteredUsers.length})
              </CardTitle>
              <CardDescription>
                Manage user accounts and permissions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex flex-1 items-center gap-4">
                  <div className="relative flex-1 max-w-sm">
                    <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      placeholder="Search users..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[140px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Status" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Status</SelectItem>
                      <SelectItem value="active">Active</SelectItem>
                      <SelectItem value="inactive">Inactive</SelectItem>
                    </SelectContent>
                  </Select>
                  <Select value={roleFilter} onValueChange={setRoleFilter}>
                    <SelectTrigger className="w-[140px]">
                      <Filter className="h-4 w-4 mr-2" />
                      <SelectValue placeholder="Role" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Roles</SelectItem>
                      <SelectItem value={UserRole.ADMIN}>Admin</SelectItem>
                      <SelectItem value={UserRole.USER}>User</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Users Table */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="rounded-md border"
          >
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Last Login</TableHead>
                  <TableHead>Created</TableHead>
                  <TableHead className="w-[50px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user, index) => (
                  <motion.tr
                    key={user.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.1 * index }}
                    className="hover:bg-muted/50 transition-colors"
                  >
                                         <TableCell>
                       <div className="flex items-center gap-3">
                         <div className="h-8 w-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-medium">
                           {user.name?.split(' ').map(n => n[0]).join('') || 'U'}
                         </div>
                         <div>
                           <p className="text-sm font-medium">{user.name}</p>
                           <p className="text-xs text-muted-foreground">{user.email}</p>
                         </div>
                       </div>
                     </TableCell>
                    <TableCell>
                      <Badge variant={getRoleBadgeVariant(user.role)}>
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge variant={getStatusBadgeVariant(user.is_active)}>
                        {user.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString() : "N/A"}
                    </TableCell>
                    <TableCell className="text-muted-foreground">
                      {new Date(user.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            onClick={() => handleEditUser(user)}
                            disabled={actionLoading !== null}
                          >
                            <Edit className="h-4 w-4 mr-2" />
                            Edit User
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                            disabled={actionLoading !== null}
                          >
                            {actionLoading === `status-${user.id}` ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                {user.is_active ? 'Deactivating...' : 'Activating...'}
                              </>
                            ) : user.is_active ? (
                              <>
                                <UserX className="h-4 w-4 mr-2" />
                                Deactivate
                              </>
                            ) : (
                              <>
                                <UserCheck className="h-4 w-4 mr-2" />
                                Activate
                              </>
                            )}
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          <DropdownMenuItem 
                            className="text-red-600"
                            onClick={() => handleDeleteUser(user.id)}
                            disabled={actionLoading !== null}
                          >
                            {actionLoading === `delete-${user.id}` ? (
                              <>
                                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                                Deleting...
                              </>
                            ) : (
                              <>
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete User
                              </>
                            )}
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </motion.tr>
                ))}
              </TableBody>
            </Table>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
} 