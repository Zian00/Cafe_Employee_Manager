import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Input, Space, Tooltip, Typography } from "antd";
import { TeamOutlined } from "@ant-design/icons";
import { AgGridReact } from "ag-grid-react";
import { themeQuartz } from "ag-grid-community";
import type { ColDef, ICellRendererParams } from "ag-grid-community";
import { useCafes, useDeleteCafe } from "../../hooks/useCafes";
import ConfirmModal from "../../components/ConfirmModal";
import type { Cafe } from "../../types/cafe";

const { Title } = Typography;

export default function CafesPage() {
  const navigate = useNavigate();
  const [locationInput, setLocationInput] = useState("");
  const [locationFilter, setLocationFilter] = useState<string | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<Cafe | null>(null);

  // Debounce: update filter 300ms after the user stops typing
  useEffect(() => {
    const timer = setTimeout(() => {
      setLocationFilter(locationInput.trim() || undefined);
    }, 300);
    return () => clearTimeout(timer);
  }, [locationInput]);

  const { data: cafes = [], isLoading } = useCafes(locationFilter);
  const { mutate: deleteCafe, isPending: isDeleting } = useDeleteCafe();

  const colDefs: ColDef<Cafe>[] = [
    {
      headerName: "Logo",
      field: "logo",
      width: 80,
      sortable: false,
      cellRenderer: ({ value }: ICellRendererParams<Cafe>) =>
        value ? (
          <img
            src={value as string}
            alt="logo"
            style={{
              height: 40,
              width: 40,
              objectFit: "cover",
              borderRadius: 4,
            }}
          />
        ) : (
          <span style={{ color: "#bbb" }}>—</span>
        ),
    },
    { headerName: "Name", field: "name", flex: 1, minWidth: 120 },
    { headerName: "Description", field: "description", flex: 2, minWidth: 160 },
    {
      headerName: "Employees",
      field: "employees",
      width: 130,
      cellRenderer: ({ value, data }: ICellRendererParams<Cafe>) => (
        <Tooltip title="Click to view employees">
          <Button
            type="link"
            icon={<TeamOutlined />}
            style={{ padding: 0, textDecoration: "underline" }}
            onClick={() => navigate(`/employees?cafe=${data?.id}`)}
          >
            {value as number}
          </Button>
        </Tooltip>
      ),
    },
    { headerName: "Location", field: "location", flex: 1, minWidth: 120 },
    {
      headerName: "Actions",
      width: 160,
      sortable: false,
      cellRenderer: ({ data }: ICellRendererParams<Cafe>) => (
        <Space>
          <Button
            size="small"
            onClick={() => navigate(`/cafes/${data?.id}/edit`)}
          >
            Edit
          </Button>
          <Button
            size="small"
            danger
            onClick={() => setDeleteTarget(data ?? null)}
          >
            Delete
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: 16,
        }}
      >
        <Title level={3} style={{ margin: 0 }}>
          Cafes
        </Title>
        <Button type="primary" onClick={() => navigate("/cafes/new")}>
          + Add New Cafe
        </Button>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Input
          placeholder="Filter by location"
          value={locationInput}
          onChange={(e) => setLocationInput(e.target.value)}
          allowClear
          style={{ width: 240 }}
        />
      </div>

      <div style={{ height: 500 }}>
        <AgGridReact
          theme={themeQuartz}
          loadThemeGoogleFonts={false}
          rowData={cafes}
          columnDefs={colDefs}
          loading={isLoading}
          rowHeight={56}
        />
      </div>

      <ConfirmModal
        open={!!deleteTarget}
        title="Delete Cafe"
        content={`Delete "${deleteTarget?.name}"? All employees under this cafe will also be deleted.`}
        onOk={() =>
          deleteTarget &&
          deleteCafe(deleteTarget.id, {
            onSuccess: () => setDeleteTarget(null),
          })
        }
        onCancel={() => setDeleteTarget(null)}
        loading={isDeleting}
      />
    </div>
  );
}
