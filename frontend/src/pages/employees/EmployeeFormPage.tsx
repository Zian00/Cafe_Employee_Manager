import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams, useBlocker } from "react-router-dom";
import { Form, Radio, Select, Typography, Spin, message } from "antd";
import {
  useEmployees,
  useCreateEmployee,
  useUpdateEmployee,
} from "../../hooks/useEmployees";
import { useCafes } from "../../hooks/useCafes";
import ReusableTextbox from "../../components/ReusableTextbox";
import FormActions from "../../components/FormActions";
import ConfirmModal from "../../components/ConfirmModal";
import type { Gender } from "../../types/employee";

const { Title } = Typography;

interface EmployeeFormValues {
  name: string;
  email_address: string;
  phone_number: string;
  gender: Gender;
  cafe_id: string | null;
}

export default function EmployeeFormPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;

  const [form] = Form.useForm<EmployeeFormValues>();
  const isDirtyRef = useRef(false);
  const [isDirty, setIsDirty] = useState(false);

  const { data: employees = [], isLoading: employeesLoading } = useEmployees();
  const { data: cafes = [] } = useCafes();
  const { mutate: createEmployee, isPending: isCreating } = useCreateEmployee();
  const { mutate: updateEmployee, isPending: isUpdating } = useUpdateEmployee();
  const isSaving = isCreating || isUpdating;

  const markDirty = () => {
    isDirtyRef.current = true;
    setIsDirty(true);
  };
  const markClean = () => {
    isDirtyRef.current = false;
    setIsDirty(false);
  };

  // Prefill form in edit mode
  useEffect(() => {
    if (isEdit && employees.length > 0) {
      const emp = employees.find((e) => e.id === id);
      if (emp) {
        form.setFieldsValue({
          name: emp.name,
          email_address: emp.email_address,
          phone_number: emp.phone_number,
          gender: emp.gender,
          cafe_id: emp.cafe_id,
        });
      }
    }
  }, [isEdit, id, employees, form]);

  // Block in-app navigation when dirty
  const blocker = useBlocker(() => isDirtyRef.current);

  // Block browser close/refresh when dirty
  useEffect(() => {
    const handler = (e: BeforeUnloadEvent) => {
      if (isDirty) e.preventDefault();
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [isDirty]);

  const onFinish = (values: EmployeeFormValues) => {
    if (isEdit) {
      updateEmployee(
        { id: id!, ...values },
        {
          onSuccess: () => {
            markClean();
            navigate("/employees");
          },
          onError: () =>
            message.error("Failed to update employee. Please try again."),
        },
      );
    } else {
      createEmployee(values, {
        onSuccess: () => {
          markClean();
          navigate("/employees");
        },
        onError: () =>
          message.error("Failed to create employee. Please try again."),
      });
    }
  };

  if (isEdit && employeesLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", padding: 64 }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 600 }}>
      <Title level={3}>{isEdit ? "Edit Employee" : "Add New Employee"}</Title>

      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        onValuesChange={markDirty}
      >
        <ReusableTextbox
          label="Name"
          name="name"
          rules={[
            { required: true, message: "Name is required." },
            { min: 6, message: "Name must be at least 6 characters." },
            { max: 10, message: "Name must not exceed 10 characters." },
          ]}
        />

        <ReusableTextbox
          label="Email Address"
          name="email_address"
          rules={[
            { required: true, message: "Email is required." },
            { type: "email", message: "Enter a valid email address." },
          ]}
        />

        <ReusableTextbox
          label="Phone Number"
          name="phone_number"
          rules={[
            { required: true, message: "Phone number is required." },
            {
              pattern: /^[89]\d{7}$/,
              message: "Phone must start with 8 or 9 and be exactly 8 digits.",
            },
          ]}
          inputProps={{ placeholder: "e.g. 81234567" }}
        />

        <Form.Item
          label="Gender"
          name="gender"
          rules={[{ required: true, message: "Gender is required." }]}
        >
          <Radio.Group>
            <Radio value="Male">Male</Radio>
            <Radio value="Female">Female</Radio>
          </Radio.Group>
        </Form.Item>

        <Form.Item label="Assigned Cafe (optional)" name="cafe_id">
          <Select
            placeholder="Select a cafe"
            allowClear
            options={cafes.map((c) => ({ value: c.id, label: c.name }))}
          />
        </Form.Item>

        <FormActions
          onCancel={() => navigate("/employees")}
          submitLabel={isEdit ? "Save Changes" : "Create Employee"}
          loading={isSaving}
        />
      </Form>

      <ConfirmModal
        open={blocker.state === "blocked"}
        title="Unsaved Changes"
        content="You have unsaved changes. Are you sure you want to leave?"
        okText="Leave"
        onOk={() => blocker.proceed?.()}
        onCancel={() => blocker.reset?.()}
      />
    </div>
  );
}
